import logging
import json
import os
import re
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

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.parent
FAQ_FILE = SCRIPT_DIR / "shared-data" / "lenskart_faq.json"
LEADS_DIR = SCRIPT_DIR / "shared-data" / "leads"

# Ensure leads directory exists
LEADS_DIR.mkdir(parents=True, exist_ok=True)

# Load FAQ data at module level for prewarming
FAQ_DATA = None


def sanitize_output(text: str) -> str:
    """Sanitize output to prevent XSS and injection attacks"""
    if not text:
        return ""
    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove script-like patterns
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    # Encode common HTML entities
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def load_faq_data():
    """Load FAQ data from JSON file"""
    global FAQ_DATA
    if FAQ_DATA is None:
        try:
            with open(FAQ_FILE, 'r', encoding='utf-8') as f:
                FAQ_DATA = json.load(f)
            logger.info("FAQ data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading FAQ data: {e}")
            FAQ_DATA = {}
    return FAQ_DATA


def search_faq(query: str) -> str:
    """Search FAQ for relevant answers using keyword matching"""
    faq_data = load_faq_data()
    query_lower = query.lower()
    
    results = []
    
    # Search in FAQ entries
    if "faq" in faq_data:
        for entry in faq_data["faq"]:
            question = entry.get("question", "").lower()
            answer = entry.get("answer", "")
            
            # Check for keyword matches
            query_words = query_lower.split()
            if any(word in question for word in query_words if len(word) > 2):
                results.append(f"Q: {entry['question']}\nA: {answer}")
    
    # Search in products
    if "products" in faq_data:
        for product in faq_data["products"]:
            product_name = product.get("name", "").lower()
            product_desc = product.get("description", "")
            
            if any(word in product_name or word in product_desc.lower() for word in query_lower.split() if len(word) > 2):
                features = ", ".join(product.get("features", [])[:3])
                results.append(f"Product: {product['name']}\nDescription: {product_desc}\nKey Features: {features}")
    
    # Search in pricing
    if "pricing" in faq_data and any(word in query_lower for word in ["price", "pricing", "cost", "fee", "charge", "free", "investment", "franchise"]):
        pricing = faq_data["pricing"]
        pricing_info = []
        
        if "eyeglasses" in pricing:
            eg = pricing["eyeglasses"]
            pricing_info.append(f"Eyeglasses: {eg.get('budget_frames', 'N/A')} (Budget), {eg.get('mid_range', 'N/A')} (Mid-range), {eg.get('premium', 'N/A')} (Premium)")
        
        if "contact_lenses" in pricing:
            cl = pricing["contact_lenses"]
            pricing_info.append(f"Contact Lenses: Daily {cl.get('daily_disposable', 'N/A')}, Monthly {cl.get('monthly_disposable', 'N/A')}")
        
        if "franchise" in pricing:
            fr = pricing["franchise"]
            pricing_info.append(f"Franchise: Total investment {fr.get('investment', 'N/A')}, Franchise fee {fr.get('franchise_fee', 'N/A')}, Royalty {fr.get('royalty', 'N/A')}")
        
        if "corporate" in pricing:
            co = pricing["corporate"]
            pricing_info.append(f"Corporate Program: {co.get('discount', 'N/A')} discount, {co.get('eye_camp', 'N/A')}")
        
        if pricing_info:
            results.append("Pricing Information:\n" + "\n".join(pricing_info))
    
    # Add company info for general questions
    if any(word in query_lower for word in ["what", "who", "about", "company", "lenskart"]) and "company" in faq_data:
        company = faq_data["company"]
        results.append(f"About {company.get('name', 'Lenskart')}: {company.get('description', '')}")
    
    if results:
        # Sanitize output to prevent injection attacks
        return sanitize_output("\n\n---\n\n".join(results[:3]))  # Return top 3 results
    
    return "I don't have specific information about that in our FAQ. Let me tell you about what Lenskart offers in general, and I can connect you with our team for detailed questions."


# SDR Persona Instructions
SDR_INSTRUCTIONS = """You are Elena, a friendly and knowledgeable Sales Development Representative (SDR) for Lenskart, India's largest eyewear brand with 2000+ stores.

PERSONALITY:
- Warm, helpful, and conversational
- Knowledgeable about eyewear and eye care
- Professional but approachable  
- Good listener who understands customer needs
- Never pushy - focuses on helping

CONVERSATION FLOW:
1. GREETING: Start with a warm greeting and introduce yourself as Elena from Lenskart
2. DISCOVERY: Ask what brings them to Lenskart today - are they looking for eyewear, interested in franchise, or corporate solutions?
3. UNDERSTAND NEEDS: Listen carefully to understand their specific needs
4. ANSWER QUESTIONS: Use the FAQ tool to answer product/pricing/franchise questions accurately
5. COLLECT LEAD INFO: Naturally gather lead information during conversation
6. SUMMARIZE & CLOSE: When they're done, summarize and offer next steps

LEAD COLLECTION - Naturally ask for these during conversation:
- Name (Ask: "May I know your name?")
- Company name (Ask: "Are you calling on behalf of a company?" - for corporate/franchise inquiries)
- Email (Ask: "What's the best email to reach you?")
- Role (Ask: "What's your role?" - for corporate inquiries)
- Use case (Understand: Are they looking for personal eyewear, franchise opportunity, or corporate program?)
- Team size (Ask: "How many employees does your company have?" - for corporate inquiries)
- Location (Ask: "Which city are you based in?" - important for franchise and store visits)
- Timeline (Ask: "When are you looking to get started?" - now/soon/exploring)

IMPORTANT RULES:
- Keep responses concise and conversational (this is a voice call)
- Don't use complex formatting, emojis, or markdown
- Use the search_faq tool to answer product/franchise/pricing questions - don't make up details
- Use the save_lead_info tool to store lead information as you collect it
- When user says "That's all", "I'm done", "Thanks, bye", "Goodbye" etc., use the generate_call_summary tool
- For franchise inquiries, mention the ₹25-35 lakh investment range
- For corporate inquiries, mention up to 40% discount and free eye camps
- Speak naturally as if on a phone call

ABOUT LENSKART:
Lenskart is India's largest eyewear company founded by Peyush Bansal in 2010. We have 2000+ stores across 300+ cities, serving over 40 million customers. We offer:
- Eyeglasses starting from ₹999 (brands: Vincent Chase, John Jacobs, Lenskart Air, Hustlr)
- Sunglasses and Contact Lenses
- Free Home Eye Checkups in 100+ cities
- Corporate Eyewear Programs (up to 40% discount for companies)
- Franchise Opportunities (₹25-35 lakh investment, 18-24 month ROI)

Our key differentiators: Affordable premium eyewear, free home eye checkups, 3D virtual try-on, BLU lenses for screen protection, and India's largest retail eyewear network."""


class SDRAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=SDR_INSTRUCTIONS,
        )
        self.lead_data = {
            "name": None,
            "company": None,
            "email": None,
            "role": None,
            "use_case": None,
            "team_size": None,
            "timeline": None,
            "location": None,
            "interests": [],
            "questions_asked": [],
            "conversation_notes": []
        }
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @function_tool
    async def search_faq(self, context: RunContext, query: str):
        """Search the Lenskart FAQ and company information to answer customer questions.
        
        Use this tool whenever the user asks about:
        - What Lenskart does or who it's for
        - Eyeglasses, sunglasses, or contact lenses
        - Pricing information
        - Franchise opportunities and investment
        - Corporate eyewear programs
        - Home eye checkup service
        - Store locations
        - Any company-related questions
        
        Args:
            query: The user's question or keywords to search for
        """
        logger.info(f"Searching FAQ for: {query}")
        result = search_faq(query)
        
        # Track the question
        self.lead_data["questions_asked"].append(query)
        
        return result
    
    @function_tool
    async def save_lead_info(
        self, 
        context: RunContext, 
        field: str,
        value: str
    ):
        """Save a piece of lead information collected during the conversation.
        
        Use this tool immediately when the user provides any of these details:
        - name: Their name
        - company: Their company name (for corporate/franchise inquiries)
        - email: Their email address
        - role: Their job role/title
        - use_case: What they're interested in (eyewear/franchise/corporate program)
        - team_size: Size of their team or company (for corporate inquiries)
        - timeline: When they want to get started (now/soon/later)
        - location: Their city or preferred location
        
        Args:
            field: The field name (name, company, email, role, use_case, team_size, timeline, location)
            value: The value to save
        """
        valid_fields = ["name", "company", "email", "role", "use_case", "team_size", "timeline", "location"]
        
        if field.lower() in valid_fields:
            self.lead_data[field.lower()] = value
            logger.info(f"Saved lead info: {field} = {value}")
            
            # Save to file after each update
            self._save_lead_to_file()
            
            return f"Saved {field}: {value}"
        else:
            return f"Unknown field: {field}"
    
    @function_tool
    async def add_conversation_note(self, context: RunContext, note: str):
        """Add a note about the conversation, such as specific pain points or interests.
        
        Use this to capture important details like:
        - Specific challenges they mentioned
        - Features they're most interested in
        - Budget constraints
        - Decision-making process
        
        Args:
            note: The note to add about the conversation
        """
        self.lead_data["conversation_notes"].append(note)
        self._save_lead_to_file()
        logger.info(f"Added conversation note: {note}")
        return "Note saved"
    
    @function_tool
    async def generate_call_summary(self, context: RunContext):
        """Generate and save the end-of-call summary.
        
        Use this tool when:
        - The user indicates they're done (says "that's all", "I'm done", "thanks bye", "goodbye", etc.)
        - The conversation is naturally concluding
        - Before saying final goodbye
        
        This will create a summary of the lead and save all collected information.
        """
        logger.info("Generating call summary")
        
        # Add timestamp
        self.lead_data["call_timestamp"] = datetime.now().isoformat()
        self.lead_data["session_id"] = self.session_id
        
        # Create summary
        summary_parts = []
        
        if self.lead_data.get("name"):
            summary_parts.append(f"Spoke with {self.lead_data['name']}")
        
        if self.lead_data.get("company"):
            summary_parts.append(f"from {self.lead_data['company']}")
        
        if self.lead_data.get("role"):
            summary_parts.append(f"({self.lead_data['role']})")
        
        summary = " ".join(summary_parts) + "." if summary_parts else "Lead information:"
        
        if self.lead_data.get("use_case"):
            summary += f" Interested in: {self.lead_data['use_case']}."
        
        if self.lead_data.get("location"):
            summary += f" Location: {self.lead_data['location']}."
        
        if self.lead_data.get("team_size"):
            summary += f" Team size: {self.lead_data['team_size']}."
        
        if self.lead_data.get("timeline"):
            summary += f" Timeline: {self.lead_data['timeline']}."
        
        if self.lead_data.get("email"):
            summary += f" Best contact: {self.lead_data['email']}."
        
        self.lead_data["summary"] = summary
        
        # Save final lead data
        self._save_lead_to_file()
        
        return f"Summary generated: {summary}"
    
    def _save_lead_to_file(self):
        """Save lead data to a JSON file"""
        try:
            lead_file = LEADS_DIR / f"lead_{self.session_id}.json"
            with open(lead_file, 'w', encoding='utf-8') as f:
                json.dump(self.lead_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Lead data saved to {lead_file}")
        except Exception as e:
            logger.error(f"Error saving lead data: {e}")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    # Prewarm FAQ data
    load_faq_data()
    logger.info("Prewarmed VAD and FAQ data")


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
        agent=SDRAssistant(),
        room=ctx.room,
        # Noise cancellation disabled for local development (requires LiveKit Cloud)
        # room_input_options=RoomInputOptions(
        #     noise_cancellation=noise_cancellation.BVC(),
        # ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
