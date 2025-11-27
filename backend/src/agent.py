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

# Load environment variables from the backend directory
ENV_PATH = Path(__file__).parent.parent / ".env.local"
load_dotenv(ENV_PATH)

# Path to the fraud cases database
FRAUD_DB_PATH = Path(__file__).parent.parent / "shared-data" / "fraud_cases.json"


def load_fraud_database():
    """Load the fraud cases from the JSON database."""
    try:
        with open(FRAUD_DB_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Fraud database not found at {FRAUD_DB_PATH}")
        return {"fraud_cases": []}


def save_fraud_database(data):
    """Save the fraud cases to the JSON database."""
    with open(FRAUD_DB_PATH, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Fraud database updated successfully")


def find_case_by_username(username: str):
    """Find a fraud case by username (case-insensitive)."""
    db = load_fraud_database()
    for case in db.get("fraud_cases", []):
        if case.get("userName", "").lower() == username.lower():
            return case
    return None


def update_case_status(username: str, status: str, outcome_note: str):
    """Update the status and outcome note of a fraud case."""
    db = load_fraud_database()
    for case in db.get("fraud_cases", []):
        if case.get("userName", "").lower() == username.lower():
            case["status"] = status
            case["outcome"] = status
            case["outcomeNote"] = outcome_note
            save_fraud_database(db)
            logger.info(f"Updated case for {username}: status={status}, note={outcome_note}")
            return True
    return False


class FraudAlertAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a fraud detection representative for SecureBank, a trusted financial institution. 
            The user is interacting with you via voice, even if you perceive the conversation as text.
            
            YOUR ROLE:
            - You are calling customers about suspicious transactions detected on their accounts
            - You are calm, professional, and reassuring
            - You must protect customer data and never ask for full card numbers, PINs, or passwords
            
            CALL FLOW:
            1. GREETING: Introduce yourself as a representative from SecureBank's Fraud Detection Department
            2. ASK FOR NAME: Ask the customer for their name to look up their account
            3. LOOKUP: Use the lookup_fraud_case tool with their name to find their case
            4. VERIFICATION: If a case is found, ask them the security question from their account to verify their identity
            5. VERIFY: Use the verify_user_identity tool to check if their answer is correct
            6. If verification FAILS: Apologize and explain you cannot proceed. Use update_case_status with status "verification_failed"
            7. If verification PASSES: Read out the suspicious transaction details (merchant name, amount, card ending, time, location)
            8. ASK CONFIRMATION: Ask if they made this transaction (yes or no)
            9. OUTCOME:
               - If YES (they made it): Use update_case_status with status "confirmed_safe" and thank them
               - If NO (they didn't make it): Use update_case_status with status "confirmed_fraud", inform them the card will be blocked and a dispute will be raised
            10. END: Summarize the action taken and end the call professionally
            
            IMPORTANT RULES:
            - Keep responses concise and clear - this is a voice call
            - Do NOT use any special formatting, asterisks, or emojis
            - Always use the tools to lookup cases, verify identity, and update status
            - Never reveal the security answer - only confirm if it's correct or not
            - Be empathetic if fraud is confirmed - reassure the customer their account is protected
            
            SAMPLE CONVERSATION:
            Agent: "Hello, this is Alex from SecureBank's Fraud Detection Department. We've detected some unusual activity on your account and I'm calling to verify a recent transaction. May I know your name please?"
            User: "John"
            [Use lookup_fraud_case tool]
            Agent: "Thank you John. For security purposes, I need to verify your identity. Can you please tell me: What is your mother's maiden name?"
            User: "Smith"
            [Use verify_user_identity tool]
            Agent: "Thank you for confirming. We've flagged a transaction of $847.99 at TechGadgets Pro, made on November 26th at 11:42 PM from Singapore, using your card ending in 4242. Did you authorize this transaction?"
            User: "No, I didn't make that purchase"
            [Use update_case_status tool with confirmed_fraud]
            Agent: "I understand this is concerning. I've marked this as a fraudulent transaction. Your card ending in 4242 has been blocked to prevent further unauthorized use, and we've initiated a dispute on your behalf. You'll receive a new card within 5-7 business days. Is there anything else I can help you with?"
            """,
        )
        self._current_case = None
    
    @function_tool
    async def lookup_fraud_case(self, context: RunContext, username: str):
        """Look up a fraud case by the customer's username.
        
        Args:
            username: The customer's name to look up in the fraud database
        """
        logger.info(f"Looking up fraud case for username: {username}")
        case = find_case_by_username(username)
        
        if case:
            self._current_case = case
            transaction = case.get("transaction", {})
            return {
                "found": True,
                "userName": case.get("userName"),
                "cardEnding": case.get("cardEnding"),
                "securityQuestion": case.get("securityQuestion"),
                "transactionName": transaction.get("name"),
                "transactionAmount": transaction.get("amount"),
                "transactionTime": transaction.get("time"),
                "transactionLocation": transaction.get("location"),
                "transactionCategory": transaction.get("category"),
                "currentStatus": case.get("status")
            }
        else:
            return {
                "found": False,
                "message": f"No pending fraud case found for {username}. Please verify the name is correct."
            }
    
    @function_tool
    async def verify_user_identity(self, context: RunContext, username: str, security_answer: str):
        """Verify the user's identity by checking their security answer.
        
        Args:
            username: The customer's name
            security_answer: The customer's answer to the security question
        """
        logger.info(f"Verifying identity for username: {username}")
        case = find_case_by_username(username)
        
        if not case:
            return {
                "verified": False,
                "reason": "No case found for this user"
            }
        
        expected_answer = case.get("securityAnswer", "").lower().strip()
        provided_answer = security_answer.lower().strip()
        
        if expected_answer == provided_answer:
            logger.info(f"Identity verified successfully for {username}")
            return {
                "verified": True,
                "message": "Identity verified successfully"
            }
        else:
            logger.warning(f"Identity verification failed for {username}")
            return {
                "verified": False,
                "reason": "Security answer does not match our records"
            }
    
    @function_tool
    async def update_case_status(self, context: RunContext, username: str, status: str, outcome_note: str):
        """Update the status of a fraud case after the call is complete.
        
        Args:
            username: The customer's name
            status: The new status - must be one of: confirmed_safe, confirmed_fraud, verification_failed
            outcome_note: A brief note describing the outcome of the call
        """
        logger.info(f"Updating case status for {username}: {status} - {outcome_note}")
        
        valid_statuses = ["confirmed_safe", "confirmed_fraud", "verification_failed"]
        if status not in valid_statuses:
            return {
                "success": False,
                "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            }
        
        success = update_case_status(username, status, outcome_note)
        
        if success:
            return {
                "success": True,
                "message": f"Case for {username} has been updated to '{status}'",
                "status": status,
                "note": outcome_note
            }
        else:
            return {
                "success": False,
                "message": f"Failed to update case for {username}. User not found in database."
            }

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline for the Fraud Alert Agent
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice - using Murf for professional, clear speech
        tts=murf.TTS(
                voice="en-US-matthew", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        preemptive_generation=True,
    )

    # Metrics collection, to measure pipeline performance
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session with the Fraud Alert Agent
    await session.start(
        agent=FraudAlertAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()
    
    # Log fraud database location for debugging
    logger.info(f"Fraud database location: {FRAUD_DB_PATH}")
    logger.info("Fraud Alert Voice Agent is ready and waiting for calls")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
