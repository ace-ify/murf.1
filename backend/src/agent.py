import logging
import json
import os
from datetime import datetime
from typing import Optional

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
from livekit.plugins import murf, silero, openai, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly Starbucks barista taking voice orders. The user is interacting with you via voice.
            
            Your job is to help customers order their perfect coffee drink by gathering the following information:
            - drinkType: The type of drink (e.g., Latte, Cappuccino, Americano, Flat White, Mocha, Caramel Macchiato, Frappuccino, Cold Brew, etc.)
            - size: The size (Tall, Grande, or Venti)
            - milk: The type of milk (Whole Milk, 2% Milk, Nonfat Milk, Almond Milk, Oat Milk, Soy Milk, Coconut Milk)
            - extras: Any add-ons or modifications (e.g., Extra Shot, Vanilla Syrup, Caramel Drizzle, Whipped Cream, Sugar-Free, Extra Hot, Iced, etc.)
            - name: The customer's name for the order
            
            Be warm, welcoming, and use Starbucks lingo naturally. Ask clarifying questions one at a time until you have all the information.
            If the customer doesn't specify something, suggest popular options. Keep responses concise and friendly.
            
            Once you have all the information, confirm the complete order with the customer, then save it using the save_order tool.
            After saving, thank them warmly and let them know their order is being prepared.""",
        )
        
        # Initialize order state
        self.order_state = {
            "drinkType": None,
            "size": None,
            "milk": None,
            "extras": [],
            "name": None
        }
    
    @function_tool
    async def save_order(
        self, 
        context: RunContext, 
        drink_type: str,
        size: str,
        milk: str,
        extras: str,
        name: str
    ):
        """Save the customer's completed coffee order to a JSON file.
        
        This tool should be called ONLY when you have collected all required information:
        drinkType, size, milk, extras (can be empty list), and name.
        
        Args:
            drink_type: The type of coffee drink (e.g., Latte, Cappuccino, Mocha)
            size: The size of the drink (Tall, Grande, or Venti)
            milk: The type of milk (e.g., Whole Milk, Oat Milk, Almond Milk)
            extras: Comma-separated list of extras or modifications (e.g., "Extra Shot, Vanilla Syrup")
            name: The customer's name for the order
        """
        
        logger.info(f"Saving order for {name}: {size} {drink_type} with {milk}")
        
        # Parse extras into a list
        extras_list = [e.strip() for e in extras.split(",")] if extras else []
        
        # Create order object
        order = {
            "drinkType": drink_type,
            "size": size,
            "milk": milk,
            "extras": extras_list,
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "orderNumber": datetime.now().strftime("%Y%m%d%H%M%S")
        }
        
        # Ensure orders directory exists
        orders_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "orders")
        os.makedirs(orders_dir, exist_ok=True)
        
        # Save to JSON file
        filename = f"order_{order['orderNumber']}_{name.replace(' ', '_')}.json"
        filepath = os.path.join(orders_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(order, f, indent=2)
        
        logger.info(f"Order saved successfully to {filepath}")
        
        return f"Order saved successfully! Order number: {order['orderNumber']}"


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
        llm=openai.LLM(
                model="gpt-4o-mini",
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
