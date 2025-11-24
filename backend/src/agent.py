import logging
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Path to wellness log file
WELLNESS_LOG_PATH = Path(__file__).parent.parent / "wellness_log.json"


def load_wellness_log():
    """Load wellness log from JSON file"""
    if not WELLNESS_LOG_PATH.exists():
        return []
    
    try:
        with open(WELLNESS_LOG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading wellness log: {e}")
        return []


def save_wellness_log(entries):
    """Save wellness log to JSON file"""
    try:
        with open(WELLNESS_LOG_PATH, 'w') as f:
            json.dump(entries, f, indent=2)
        logger.info(f"Wellness log saved to {WELLNESS_LOG_PATH}")
    except Exception as e:
        logger.error(f"Error saving wellness log: {e}")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a supportive and grounded health and wellness voice companion. Your role is to conduct daily check-ins with users about their mood, energy, and daily goals.

Your approach:
- Be warm, empathetic, and supportive, but realistic and non-judgmental
- Ask about mood and energy levels in a conversational way
- Help users identify 1-3 practical objectives or intentions for the day
- Offer simple, actionable, and grounded advice (not medical or diagnostic)
- Reference past check-ins when available to show continuity
- Keep advice small and realistic (like taking short breaks, breaking tasks into steps, simple grounding exercises)
- Close each check-in with a brief recap of mood and objectives
- Encourage the user to confirm if the recap sounds right

Remember:
- You are NOT a clinician or therapist - you're a supportive companion
- Avoid medical diagnoses or clinical advice
- Keep conversations concise and voice-friendly
- No complex formatting, emojis, or special characters in your responses
- Your responses should sound natural when spoken aloud

When the user confirms their check-in is complete, use the save_checkin tool to persist the data.
If you need to reference past check-ins, use the get_past_checkins tool.""",
        )

    @function_tool
    async def save_checkin(
        self,
        context: RunContext,
        mood: str,
        energy: str,
        objectives: str,
        summary: str = ""
    ):
        """Save the current wellness check-in to the log file.
        
        Use this tool when the user has shared their mood, energy level, and daily objectives,
        and you have provided a recap that they've confirmed.
        
        Args:
            mood: The user's reported mood (e.g., "feeling good", "a bit stressed", "low energy")
            energy: The user's energy level (e.g., "high", "medium", "low", "tired but motivated")
            objectives: The user's stated objectives or intentions for the day (list 1-3 items)
            summary: An optional brief summary sentence about this check-in
        """
        logger.info(f"Saving wellness check-in: mood={mood}, energy={energy}")
        
        # Load existing entries
        entries = load_wellness_log()
        
        # Create new entry
        new_entry = {
            "date": datetime.now().isoformat(),
            "mood": mood,
            "energy": energy,
            "objectives": objectives,
            "summary": summary or f"Check-in on {datetime.now().strftime('%B %d, %Y')}"
        }
        
        # Add to log
        entries.append(new_entry)
        
        # Save back to file
        save_wellness_log(entries)
        
        return f"Check-in saved successfully. I've recorded your mood, energy level, and objectives for today."

    @function_tool
    async def get_past_checkins(self, context: RunContext, days: int = 7):
        """Retrieve past wellness check-ins from the log.
        
        Use this tool at the start of a conversation to reference previous check-ins,
        or when the user asks about their history or trends.
        
        Args:
            days: Number of recent days to retrieve (default 7)
        """
        logger.info(f"Retrieving past {days} days of check-ins")
        
        entries = load_wellness_log()
        
        if not entries:
            return "This is your first check-in. Welcome!"
        
        # Get the most recent entries
        recent_entries = entries[-days:] if len(entries) > days else entries
        
        # Format the entries for the LLM
        formatted = []
        for entry in recent_entries:
            date_str = datetime.fromisoformat(entry['date']).strftime('%B %d, %Y')
            formatted.append(
                f"Date: {date_str}\n"
                f"Mood: {entry['mood']}\n"
                f"Energy: {entry['energy']}\n"
                f"Objectives: {entry['objectives']}"
            )
        
        return "Past check-ins:\n\n" + "\n\n".join(formatted)


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-US-matthew", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
