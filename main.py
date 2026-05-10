import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import AgentState
from src.agents.input_parser_agent import input_parser_node
from src.agents.intent_detection_agent import intent_detection_node
from src.agents.tone_stylist_agent import tone_stylist_node
from src.agents.draft_writer_agent import draft_writer_node
from src.agents.personalization_agent import personalization_node
from src.agents.review_agent import review_node
from src.agents.router_agent import route_after_review


def build_workflow():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("❌ OPENAI_API_KEY is missing from the environment or .env file.")

    workflow = StateGraph(AgentState)
    workflow.add_node("parser", input_parser_node)
    workflow.add_node("intent", intent_detection_node)
    workflow.add_node("stylist", tone_stylist_node)
    workflow.add_node("personalizer", personalization_node)
    workflow.add_node("writer", draft_writer_node)
    workflow.add_node("reviewer", review_node)

    workflow.set_entry_point("parser")
    workflow.add_edge("parser", "intent")
    workflow.add_edge("intent", "stylist")
    workflow.add_edge("stylist", "personalizer")
    workflow.add_edge("personalizer", "writer")
    workflow.add_edge("writer", "reviewer")

    workflow.add_conditional_edges(
        "reviewer",
        route_after_review,
        {
            "rewrite": "writer",
            "end": END
        }
    )

    return workflow.compile(checkpointer=MemorySaver())


def run_sample():
    app = build_workflow()
    config = {"configurable": {"thread_id": "main_example"}}
    inputs = {
        "user_prompt": "Update the team about the upcoming client demo schedule change.",
        "recipient": "Team",
        "tone": "Informative and Polite",
        "email_subject": "Client Demo Schedule Update"
    }

    result = app.invoke(inputs, config)
    print("Subject:", inputs["email_subject"])
    print("Draft:\n")
    print(result.get("draft", "No draft generated."))


if __name__ == "__main__":
    run_sample()
