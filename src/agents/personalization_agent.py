import json
import os
from src.state import AgentState

PERSONALIZATION_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 
                                    'data', 'personalization.json')

def personalization_node(state: AgentState) -> dict:
    """Loads and injects user-specific profile context from JSON storage."""
    
    print("🔹 [Personalization Agent] Loading user profile data...")
    
    personalized_context = "No personalization data available."
    
    if os.path.exists(PERSONALIZATION_FILE):
        try:
            with open(PERSONALIZATION_FILE, 'r') as f:
                data = json.load(f)
                company = data.get('company', 'Unknown Company')
                name = data.get('name', 'Unknown User')
                style = data.get('style', 'Professional')
                
                personalized_context = (
                    f"User profile: Name is {name}, works at {company}, "
                    f"prefers {style} communication style. "
                    "Reference past successful interactions and maintain consistency with preferred style."
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading personalization data: {e}")
    else:
        print(f"Personalization file not found at {PERSONALIZATION_FILE}. Using default context.")
    
    return {"personalized_context": personalized_context}
