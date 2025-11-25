import logging
import json
import os
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

# Load tutor content
def load_tutor_content():
    content_path = Path(__file__).parent.parent / "shared-data" / "day4_tutor_content.json"
    with open(content_path, 'r') as f:
        return json.load(f)

TUTOR_CONTENT = load_tutor_content()


class GreeterAgent(Agent):
    """Initial agent that greets the user and asks for their preferred learning mode"""
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly tutor greeting the user. Welcome them to the Active Recall Coach.
            Explain that you offer three learning modes:
            1. LEARN mode - where you explain programming concepts to them
            2. QUIZ mode - where you ask them questions to test their knowledge
            3. TEACH BACK mode - where they explain concepts back to you
            
            Ask them which mode they'd like to start with. Keep your greeting brief and conversational.
            When they choose a mode, immediately use the transfer_to_mode tool to switch them to that mode.
            If they're unsure, you can recommend starting with LEARN mode.""",
        )

    @function_tool
    async def transfer_to_learn_mode(self, context: RunContext):
        """Transfer the user to LEARN mode where concepts are explained to them.
        
        Use this when the user wants to learn about programming concepts.
        """
        logger.info("Transferring to LEARN mode")
        return LearnAgent(), "Transferring you to Learn mode with Matthew"
        
    @function_tool
    async def transfer_to_quiz_mode(self, context: RunContext):
        """Transfer the user to QUIZ mode where they answer questions.
        
        Use this when the user wants to be quizzed on programming concepts.
        """
        logger.info("Transferring to QUIZ mode")
        return QuizAgent(), "Transferring you to Quiz mode with Alicia"
        
    @function_tool
    async def transfer_to_teach_back_mode(self, context: RunContext):
        """Transfer the user to TEACH BACK mode where they explain concepts.
        
        Use this when the user wants to teach concepts back to test their understanding.
        """
        logger.info("Transferring to TEACH BACK mode")
        return TeachBackAgent(), "Transferring you to Teach Back mode with Ken"


class LearnAgent(Agent):
    """Agent that explains programming concepts (Matthew voice)"""
    def __init__(self) -> None:
        concepts_list = ", ".join([c["title"] for c in TUTOR_CONTENT])
        super().__init__(
            instructions=f"""You are Matthew, a patient and clear programming tutor in LEARN mode.
            
            Your role is to explain programming concepts clearly and engagingly. Available concepts: {concepts_list}
            
            When the user asks about a concept, explain it thoroughly but conversationally. Use examples and analogies.
            After explaining, ask if they'd like to hear about another concept, switch to QUIZ mode to test their knowledge, 
            or try TEACH BACK mode to explain it themselves.
            
            If they want to switch modes, use the appropriate transfer tool immediately.
            Keep explanations clear but not too long - aim for 30-45 seconds of speaking.""",
            tts=murf.TTS(
                voice="en-US-matthew", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        )

    @function_tool
    async def get_concept_explanation(self, context: RunContext, concept_name: str):
        """Get a detailed explanation of a programming concept.
        
        Args:
            concept_name: The name of the concept to explain (e.g., 'variables', 'loops', 'functions')
        """
        logger.info(f"Getting explanation for concept: {concept_name}")
        
        # Find the concept (case-insensitive)
        concept = next((c for c in TUTOR_CONTENT if c["title"].lower() == concept_name.lower() or c["id"].lower() == concept_name.lower()), None)
        
        if concept:
            return f"Here's what you need to know about {concept['title']}: {concept['summary']}"
        else:
            available = ", ".join([c["title"] for c in TUTOR_CONTENT])
            return f"I don't have information about that concept. Available topics are: {available}"

    @function_tool
    async def transfer_to_quiz_mode(self, context: RunContext):
        """Transfer the user to QUIZ mode to test their knowledge.
        
        Use this when the user wants to be quizzed.
        """
        logger.info("Transferring from LEARN to QUIZ mode")
        return QuizAgent(), "Transferring you to Quiz mode"
        
    @function_tool
    async def transfer_to_teach_back_mode(self, context: RunContext):
        """Transfer the user to TEACH BACK mode where they explain concepts.
        
        Use this when the user wants to teach back what they learned.
        """
        logger.info("Transferring from LEARN to TEACH BACK mode")
        return TeachBackAgent(), "Transferring you to Teach Back mode"


class QuizAgent(Agent):
    """Agent that quizzes the user (Alicia voice)"""
    def __init__(self) -> None:
        concepts_list = ", ".join([c["title"] for c in TUTOR_CONTENT])
        super().__init__(
            instructions=f"""You are Alicia, an encouraging quiz master in QUIZ mode.
            
            Your role is to ask questions about programming concepts and provide feedback on answers. 
            Available concepts: {concepts_list}
            
            Ask clear, focused questions about concepts. After they answer, provide constructive feedback - 
            praise correct answers and gently correct misconceptions with the right information.
            
            Offer to ask another question, switch to LEARN mode if they need more explanation, 
            or move to TEACH BACK mode for deeper practice.
            
            If they want to switch modes, use the appropriate transfer tool immediately.
            Be encouraging and supportive!""",
            tts=murf.TTS(
                voice="en-US-alicia", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        )

    @function_tool
    async def get_quiz_question(self, context: RunContext, concept_name: str):
        """Get a quiz question about a programming concept.
        
        Args:
            concept_name: The name of the concept to quiz on (e.g., 'variables', 'loops', 'functions')
        """
        logger.info(f"Getting quiz question for concept: {concept_name}")
        
        concept = next((c for c in TUTOR_CONTENT if c["title"].lower() == concept_name.lower() or c["id"].lower() == concept_name.lower()), None)
        
        if concept:
            return f"Here's your question about {concept['title']}: {concept['sample_question']}"
        else:
            available = ", ".join([c["title"] for c in TUTOR_CONTENT])
            return f"I don't have a question about that topic. Available topics are: {available}"

    @function_tool
    async def transfer_to_learn_mode(self, context: RunContext):
        """Transfer the user to LEARN mode to review concepts.
        
        Use this when the user needs more explanation or wants to learn.
        """
        logger.info("Transferring from QUIZ to LEARN mode")
        return LearnAgent(), "Transferring you to Learn mode"
        
    @function_tool
    async def transfer_to_teach_back_mode(self, context: RunContext):
        """Transfer the user to TEACH BACK mode where they explain concepts.
        
        Use this when the user wants to teach back what they learned.
        """
        logger.info("Transferring from QUIZ to TEACH BACK mode")
        return TeachBackAgent(), "Transferring you to Teach Back mode"


class TeachBackAgent(Agent):
    """Agent that listens to user explanations and provides feedback (Ken voice)"""
    def __init__(self) -> None:
        concepts_list = ", ".join([c["title"] for c in TUTOR_CONTENT])
        super().__init__(
            instructions=f"""You are Ken, an attentive listener and coach in TEACH BACK mode.
            
            Your role is to ask the user to explain programming concepts back to you, then provide constructive feedback.
            Available concepts: {concepts_list}
            
            Invite them to explain a concept in their own words. Listen carefully to their explanation, 
            then provide specific feedback on what they got right and what could be improved or clarified.
            
            Be supportive and highlight their strengths while gently correcting any misconceptions.
            After feedback, offer to hear another explanation, switch to LEARN mode for review, 
            or try QUIZ mode for variety.
            
            If they want to switch modes, use the appropriate transfer tool immediately.
            Remember: the best way to learn is to teach!""",
            tts=murf.TTS(
                voice="en-US-ken", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        )

    @function_tool
    async def get_concept_for_teaching(self, context: RunContext, concept_name: str):
        """Get information about a concept for the user to teach back.
        
        Args:
            concept_name: The name of the concept the user will explain (e.g., 'variables', 'loops', 'functions')
        """
        logger.info(f"Preparing concept for teach-back: {concept_name}")
        
        concept = next((c for c in TUTOR_CONTENT if c["title"].lower() == concept_name.lower() or c["id"].lower() == concept_name.lower()), None)
        
        if concept:
            return f"Great! Please explain {concept['title']} to me in your own words. Take your time and share what you understand about this concept."
        else:
            available = ", ".join([c["title"] for c in TUTOR_CONTENT])
            return f"I don't have that topic. Available topics are: {available}"

    @function_tool
    async def evaluate_explanation(self, context: RunContext, concept_name: str, user_explanation: str):
        """Evaluate the user's explanation of a concept and provide feedback.
        
        Args:
            concept_name: The concept being explained
            user_explanation: What the user said about the concept
        """
        logger.info(f"Evaluating user explanation for: {concept_name}")
        
        concept = next((c for c in TUTOR_CONTENT if c["title"].lower() == concept_name.lower() or c["id"].lower() == concept_name.lower()), None)
        
        if concept:
            return f"Here's the key information about {concept['title']} to compare with: {concept['summary']}. Use this to provide specific, encouraging feedback on their explanation."
        else:
            return "I don't have reference information for that concept."

    @function_tool
    async def transfer_to_learn_mode(self, context: RunContext):
        """Transfer the user to LEARN mode to review concepts.
        
        Use this when the user needs more explanation or wants to learn.
        """
        logger.info("Transferring from TEACH BACK to LEARN mode")
        return LearnAgent(), "Transferring you to Learn mode"
        
    @function_tool
    async def transfer_to_quiz_mode(self, context: RunContext):
        """Transfer the user to QUIZ mode to test their knowledge differently.
        
        Use this when the user wants to try quiz mode.
        """
        logger.info("Transferring from TEACH BACK to QUIZ mode")
        return QuizAgent(), "Transferring you to Quiz mode"




def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Create the initial session
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    # Start with the greeter agent
    await session.start(
        agent=GreeterAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))

