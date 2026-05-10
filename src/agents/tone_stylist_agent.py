from langchain_openai import ChatOpenAI
from src.agents.state import AgentState

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

def tone_stylist_node(state: AgentState) -> dict:
    """Defines and sharpens tone guidelines."""
    print("🔹 [Tone Stylist Agent] Defining stylistic constraints...")
    prompt = (
        f"Describe exactly how a '{state['tone']}' email should sound in 1 sentence. "
        f"Keep it as a style guideline."
    )
    response = llm.invoke(prompt)
    return {
        "tone": state["tone"],
        "tone_guidelines": response.content.strip()
    }
