from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from src.agents.state import AgentState

# Load environment variables
load_dotenv()

# Initialize LLM if API key is available
llm = None
if os.getenv('OPENAI_API_KEY'):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
else:
    print("Warning: OPENAI_API_KEY not found in draft_writer_agent.")

# Predefined tone-aware templates
TONE_TEMPLATES = {
    "Professional": (
        "Write a professional email with subject '{email_subject}' to {recipient} regarding '{intent}'.\n"
        "Use formal language, maintain a respectful tone, and ensure clarity.\n"
        "Urgency level: {urgency}.\n"
        "Key topics to cover: {key_topics}.\n"
        "Personalized context: {personalized_context}.\n"
        "User request: {user_prompt}.\n"
        "Structure the email with a proper greeting, body, and closing."
    ),
    "Casual": (
        "Write a casual, friendly email with subject '{email_subject}' to {recipient} about '{intent}'.\n"
        "Use relaxed language, like chatting with a friend, but keep it appropriate.\n"
        "Urgency level: {urgency}.\n"
        "Key topics to cover: {key_topics}.\n"
        "Personalized context: {personalized_context}.\n"
        "User request: {user_prompt}.\n"
        "Make it conversational and engaging."
    ),
    "Direct and Urgent": (
        "Write a direct and urgent email with subject '{email_subject}' to {recipient} concerning '{intent}'.\n"
        "Be concise, assertive, and emphasize the time-sensitive nature.\n"
        "Urgency level: {urgency}.\n"
        "Key topics to cover: {key_topics}.\n"
        "Personalized context: {personalized_context}.\n"
        "User request: {user_prompt}.\n"
        "Get to the point quickly and include clear calls to action."
    ),
    "Informative and Polite": (
        "Write an informative yet polite email with subject '{email_subject}' to {recipient} about '{intent}'.\n"
        "Provide details clearly and courteously, balancing information with friendliness.\n"
        "Urgency level: {urgency}.\n"
        "Key topics to cover: {key_topics}.\n"
        "Personalized context: {personalized_context}.\n"
        "User request: {user_prompt}.\n"
        "Ensure the email is helpful and well-structured."
    )
}

def draft_writer_node(state: AgentState) -> dict:
    """Generates the email body text using tone-aware templates."""
    print("🔹 [Draft Writer Agent] Composing draft...")
    feedback = state.get("review_feedback", "")
    
    if feedback and state.get("revision_count", 0) > 0:
        prompt = (
            f"Revise this email draft for {state['recipient']} with subject '{state.get('email_subject', '')}':\n\n"
            f"Current Draft: {state['draft']}\n\n"
            f"Reviewer Feedback: {feedback}\n"
            "Apply the changes strictly."
        )
    else:
        tone = state.get('tone', 'Professional')
        base_tone = tone.split(" (")[0] if " (" in tone else tone
        template = TONE_TEMPLATES.get(base_tone, TONE_TEMPLATES['Professional'])
        tone_guidelines = state.get('tone_guidelines', '')
        
        prompt = template.format(
            recipient=state['recipient'],
            intent=state['intent'],
            urgency=state.get('urgency', 'Medium'),
            key_topics=', '.join(state.get('key_topics', [])),
            personalized_context=state.get('personalized_context', 'N/A'),
            user_prompt=state['user_prompt'],
            email_subject=state.get('email_subject', '')
        )
        
        if tone_guidelines:
            prompt += f"\n\nStyle guidelines: {tone_guidelines}"
    
    response = llm.invoke(prompt)
    return {
        "draft": response.content,
        "revision_count": state.get("revision_count", 0) + 1
    }