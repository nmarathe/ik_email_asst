from typing import TypedDict, List

class AgentState(TypedDict):
    """The shared, single source of truth for the entire agent pipeline."""
    user_prompt: str
    recipient: str
    tone: str
    email_subject: str
    key_topics: List[str]
    urgency: str
    intent: str
    tone_guidelines: str
    personalized_context: str
    draft: str
    review_feedback: str
    is_valid: bool
    revision_count: int