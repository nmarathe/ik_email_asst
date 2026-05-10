from langchain_openai import ChatOpenAI
from src.state import AgentState

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def intent_detection_node(state: AgentState) -> dict:
    """Identifies the core goal of the email."""
    print("🔹 [Intent Detection Agent] Classifying prompt goal...")
    prompt = (
        f"Identify the core intent (e.g., 'Meeting Request', 'Follow-up', 'Project Update') "
        f"from this prompt: '{state['user_prompt']}'. Respond in 3 words or less."
    )
    response = llm.invoke(prompt)
    return {"intent": response.content.strip()}
