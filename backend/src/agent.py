import logging

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

from pathlib import Path

logger = logging.getLogger("agent")

# Load .env.local from the backend directory (one level up from src)
env_path = Path(__file__).parent.parent / ".env.local"
load_dotenv(dotenv_path=env_path)


class ImprovGame:
    def __init__(self):
        self.player_name = None
        self.current_round = 0
        self.max_rounds = 3
        self.history = []  # To store round summaries: {"scenario": str, "reaction": str}
        self.scenarios = [
            "You are a time-travelling tour guide explaining modern smartphones to someone from the 1800s.",
            "You are a restaurant waiter who must calmly tell a customer that their order has escaped the kitchen.",
            "You are a customer trying to return an obviously cursed object to a very skeptical shop owner.",
            "You are a cat trying to convince a dog that you are actually a small, weird-looking dog.",
            "You are an alien trying to order a pizza but you only know words from Shakespeare plays."
        ]

    @property
    def is_game_over(self):
        return self.current_round >= self.max_rounds

    def get_next_scenario(self):
        if self.current_round < len(self.scenarios):
            return self.scenarios[self.current_round]
        return None

    def advance_round(self):
        self.current_round += 1

    def add_history(self, scenario, reaction):
        self.history.append({"scenario": scenario, "reaction": reaction})


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are the charismatic and witty host of a TV improv show called 'Improv Battle'.
            
            Your goal is to guide the player through a series of improv challenges.
            
            **Your Style:**
            - High-energy, fun, and clear about the rules.
            - You react to the player's performance with a mix of amusement, surprise, and light teasing.
            - You are NEVER mean, but you are honest. If a performance was flat, say so (gently). If it was great, celebrate it!
            
            **The Game Flow:**
            1.  **Intro:** Welcome the player to "Improv Battle". Ask for their name if you don't know it.
            2.  **The Setup:** Present a scenario clearly. Tell them who they are and what the situation is.
            3.  **The Act:** Listen to them perform.
            4.  **The Reaction:** React to their performance. Be specific about what they said.
            5.  **Next Round:** Move to the next scenario until the game is over.
            6.  **Finale:** Give a summary of their improv style and say goodbye.
            
            Always keep the show moving!""",
        )
        self.game = ImprovGame()

    @function_tool
    async def start_game(self, context: RunContext, player_name: str):
        """
        Start the improv game. Call this after the user provides their name.
        Returns the first scenario.
        """
        self.game.player_name = player_name
        scenario = self.game.get_next_scenario()
        return f"Welcome {player_name}! Here is your first scenario: {scenario}"

    @function_tool
    async def next_round(self, context: RunContext, reaction: str):
        """
        Call this after you have reacted to the player's performance.
        Args:
            reaction: A brief summary of your reaction to the player's performance.
        """
        # Get the scenario we just finished
        scenario_just_played = self.game.get_next_scenario()
        
        # Save history
        self.game.add_history(scenario_just_played, reaction)
        
        # Move forward
        self.game.advance_round()
        
        # Check status
        if self.game.is_game_over:
            return "GAME_OVER. Please call get_game_summary to wrap up."
            
        # Get new scenario
        next_scen = self.game.get_next_scenario()
        return f"Next Scenario: {next_scen}"

    @function_tool
    async def get_game_summary(self, context: RunContext):
        """
        Call this when the game is over to get a summary of the session.
        """
        return f"Game History: {self.game.history}"


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
