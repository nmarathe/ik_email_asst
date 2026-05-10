import os
import json
from dotenv import load_dotenv
from src.state import AgentState
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Initialize LLM if API key is available
llm = None
if os.getenv('OPENAI_API_KEY'):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
else:
    print("Warning: OPENAI_API_KEY not found, using fallback parsing.")

def input_parser_node(state: AgentState) -> dict:
    """Normalizes and parses user input for context consistency."""
    
    print("[Input Parser Agent] Normalizing context and extracting structured data...")
    
    user_prompt = state.get("user_prompt", "")
    recipient = state.get("recipient", "")
    tone = state.get("tone", "")
    
    # Use LLM to parse and normalize inputs
    prompt = f"""
    Analyze the following email request and extract/normalize key information:
    
    User Prompt: "{user_prompt}"
    Provided Recipient: "{recipient}"
    Provided Tone: "{tone}"
    
    Please provide:
    1. Normalized Recipient: Capitalize names, handle multiple recipients (e.g., "John Doe, Jane Smith"), or extract from prompt if not provided.
    2. Inferred Tone: If tone not provided, infer from prompt (e.g., Professional, Casual, Urgent). Use provided tone if available.
    3. Key Topics: Extract 2-3 main topics or keywords from the prompt.
    4. Urgency Level: Low, Medium, High based on prompt content.
    
    Respond in JSON format with keys: recipient, tone, topics, urgency.
    """
    
    if llm:
        try:
            response = llm.invoke(prompt)
            parsed = json.loads(response.content.strip())
            
            normalized_recipient = parsed.get("recipient", recipient or "Recipient")
            normalized_tone = parsed.get("tone", tone or "Professional")
            topics = parsed.get("topics", [])
            urgency = parsed.get("urgency", "Medium")
        except Exception as e:
            print(f"LLM parsing failed, using fallback: {e}")
            normalized_recipient = recipient or "Recipient"
            normalized_tone = tone or "Professional"
            topics = []
            urgency = "Medium"
            if "urgent" in user_prompt.lower():
                urgency = "High"
            if "casual" in user_prompt.lower():
                normalized_tone = "Casual"
    else:
        # Fallback parsing without LLM
        normalized_recipient = recipient or "Recipient"
        normalized_tone = tone or "Professional"
        topics = []
        urgency = "Medium"
        if "urgent" in user_prompt.lower():
            urgency = "High"
        if "casual" in user_prompt.lower():
            normalized_tone = "Casual"
    
    return {
        "recipient": normalized_recipient,
        "tone": normalized_tone,
        "key_topics": topics,
        "urgency": urgency,
        "revision_count": state.get("revision_count", 0)
    }
