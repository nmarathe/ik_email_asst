from langgraph.graph import END
from src.state import AgentState

def route_after_review(state: AgentState) -> str:
    """Decides if the pipeline loop continues or exits."""
    if state.get("is_valid", False):
        print("✅ [Router] Draft passed review. Completing workflow.")
        return "end"
    
    if state.get("revision_count", 0) >= 3:
        print("⚠️ [Router] Max revisions reached. Exiting graph.")
        return "end"
        
    print(f"🔄 [Router] Review failed (Attempt {state['revision_count']}). Routing back to Writer.")
    return "rewrite"