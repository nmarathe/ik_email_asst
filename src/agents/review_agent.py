from langchain_openai import ChatOpenAI
from src.state import AgentState

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def review_node(state: AgentState) -> dict:
    """Reviews draft quality and tone alignment."""
    print("🔹 [Review & Validation Agent] Evaluating quality, tone, and grammar...")
    prompt = (
        f"Analyze this email draft for the following criteria:\n"
        f"- Intent match to: {state['intent']}\n"
        f"- Tone alignment with the requested style or mood\n"
        f"- Grammar, spelling, punctuation, and clarity\n"
        f"- Overall professionalism and readability\n\n"
        f"Draft: {state['draft']}\n"
        f"Intent: {state['intent']}\n\n"
        "If it meets all requirements, say 'VALID'. "
        "Otherwise, say 'REJECTED' followed by a short line of feedback."
    )
    response = llm.invoke(prompt)
    is_valid = "VALID" in response.content.upper()
    
    return {
        "review_feedback": response.content.strip(),
        "is_valid": is_valid
    }
