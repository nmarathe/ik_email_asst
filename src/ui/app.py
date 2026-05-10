import sys
from pathlib import Path
import os

# Dynamically resolve and inject the project root into Python's path.
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

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


def setup_page():
    st.set_page_config(page_title="Email Copilot", page_icon="✉️", layout="wide")
    st.title("✉️ Email Copilot")
    st.write(
        "A chat-style email assistant for writing and refining emails. "
        "Provide recipient, subject, tone, and the request, then give feedback to update the draft."
    )


@st.cache_resource
def compile_graph():
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

    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


def initialize_state():
    defaults = {
        "recipient": "",
        "email_subject": "",
        "tone": "Professional",
        "user_prompt": "",
        "final_output": None,
        "chat_history": [],
        "feedback_input": "",
        "reset_flag": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def build_user_message():
    recipient = st.session_state.recipient or "Recipient"
    subject = st.session_state.email_subject or ""
    tone = st.session_state.tone or "Professional"
    prompt = st.session_state.user_prompt or ""

    lines = [
        f"**Recipient:** {recipient}",
        f"**Subject:** {subject}",
        f"**Tone:** {tone}",
        "",
        f"{prompt}"
    ]
    return "\n".join(lines)


def display_chat_history():
    history_container = st.container()
    with history_container:
        for item in st.session_state.chat_history:
            with st.chat_message(item["role"]):
                st.markdown(item["content"])


def clear_conversation():
    for key in [
        "recipient",
        "email_subject",
        "tone",
        "user_prompt",
        "final_output",
        "chat_history",
        "feedback_input"
    ]:
        if key in st.session_state:
            del st.session_state[key]


def revise_email():
    feedback = st.session_state.feedback_input.strip()
    if not feedback:
        st.warning("Please enter feedback before requesting a revision.")
        return
    app = compile_graph()
    revision_inputs = {
        "user_prompt": st.session_state.user_prompt,
        "recipient": st.session_state.recipient or "Recipient",
        "tone": st.session_state.tone,
        "email_subject": st.session_state.email_subject or "",
        "key_topics": st.session_state.final_output.get("key_topics", []),
        "urgency": st.session_state.final_output.get("urgency", "Medium"),
        "intent": st.session_state.final_output.get("intent", ""),
        "tone_guidelines": st.session_state.final_output.get("tone_guidelines", ""),
        "personalized_context": st.session_state.final_output.get("personalized_context", ""),
        "draft": st.session_state.final_output.get("draft", ""),
        "review_feedback": feedback,
        "is_valid": False,
        "revision_count": st.session_state.final_output.get("revision_count", 1) + 1
    }
    revision_config = {"configurable": {"thread_id": "email_chat_revision"}}

    with st.spinner("Updating the draft with your feedback..."):
        revised_output = app.invoke(revision_inputs, revision_config)

    st.session_state.final_output = revised_output
    st.session_state.chat_history.append(
        {"role": "user", "content": f"**Feedback:** {feedback}"}
    )
    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": (
                f"**Draft version {len([m for m in st.session_state.chat_history if m['role'] == 'assistant']) + 1}**\n\n"
                f"**Subject:** {st.session_state.email_subject or 'No subject'}\n\n"
                f"{revised_output.get('draft', 'No revised email generated.')}"
            )
        }
    )
    st.session_state.feedback_input = ""


def reset_conversation():
    st.session_state.reset_flag = True


def revise_email():
    feedback = st.session_state.feedback_input.strip()
    if not feedback:
        st.warning("Please enter feedback before requesting a revision.")
        return
    app = compile_graph()
    revision_inputs = {
        "user_prompt": st.session_state.user_prompt,
        "recipient": st.session_state.recipient or "Recipient",
        "tone": st.session_state.tone,
        "email_subject": st.session_state.email_subject or "",
        "key_topics": st.session_state.final_output.get("key_topics", []),
        "urgency": st.session_state.final_output.get("urgency", "Medium"),
        "intent": st.session_state.final_output.get("intent", ""),
        "tone_guidelines": st.session_state.final_output.get("tone_guidelines", ""),
        "personalized_context": st.session_state.final_output.get("personalized_context", ""),
        "draft": st.session_state.final_output.get("draft", ""),
        "review_feedback": feedback,
        "is_valid": False,
        "revision_count": st.session_state.final_output.get("revision_count", 1) + 1
    }
    revision_config = {"configurable": {"thread_id": "email_chat_revision"}}

    with st.spinner("Updating the draft with your feedback..."):
        revised_output = app.invoke(revision_inputs, revision_config)

    st.session_state.final_output = revised_output
    st.session_state.chat_history.append(
        {"role": "user", "content": f"**Feedback:** {feedback}"}
    )
    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": (
                f"**Draft version {len([m for m in st.session_state.chat_history if m['role'] == 'assistant']) + 1}**\n\n"
                f"**Subject:** {st.session_state.email_subject or 'No subject'}\n\n"
                f"{revised_output.get('draft', 'No revised email generated.')}"
            )
        }
    )
    st.session_state.feedback_input = ""


def run_ui():
    setup_page()
    initialize_state()

    if st.session_state.get("reset_flag", False):
        clear_conversation()
        st.session_state.reset_flag = False
        st.rerun()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ `OPENAI_API_KEY` is missing from your `.env` file.")
        st.stop()

    app = compile_graph()

    with st.form("email_writer_form"):
        st.text_input("Recipient", placeholder="e.g., Sarah or Team", key="recipient")
        st.text_input("Email Subject", placeholder="e.g., Demo schedule update", key="email_subject")
        st.selectbox(
            "Tone",
            ["Professional", "Direct and Urgent", "Informative and Polite", "Casual"],
            key="tone"
        )
        st.text_area(
            "Email Brief",
            placeholder="Describe what you want the email to say, including any important details.",
            key="user_prompt",
            height=180
        )
        submit_button = st.form_submit_button("🚀 Generate Email")

    if submit_button:
        if not st.session_state.user_prompt.strip():
            st.warning("Please enter your email brief before generating the draft.")
        else:
            inputs = {
                "user_prompt": st.session_state.user_prompt,
                "recipient": st.session_state.recipient or "Recipient",
                "tone": st.session_state.tone,
                "email_subject": st.session_state.email_subject or ""
            }
            config = {"configurable": {"thread_id": "email_chat_session"}}

            with st.spinner("Generating your first draft..."):
                output = app.invoke(inputs, config)

            st.session_state.final_output = output
            st.session_state.chat_history = [
                {"role": "user", "content": build_user_message()},
                {
                    "role": "assistant",
                    "content": (
                        f"**Draft version 1**\n\n"
                        f"**Subject:** {st.session_state.email_subject or 'No subject'}\n\n"
                        f"{output.get('draft', 'No email draft generated.')}"
                    )
                }
            ]
            st.session_state.feedback_input = ""

    if st.session_state.final_output:
        display_chat_history()

        st.markdown("---")
        st.subheader("✍️ Feedback & Revision")
        st.text_area(
            "What changes would you like?",
            value=st.session_state.feedback_input,
            placeholder="e.g., Make it shorter, use a warmer opening, add a call to action.",
            key="feedback_input",
            height=140
        )

        cols = st.columns([1, 1, 1])
        with cols[0]:
            st.button("🔄 Apply Feedback", on_click=revise_email)
        with cols[1]:
            st.download_button(
                label="📥 Download Latest Draft",
                data=(
                    f"Subject: {st.session_state.email_subject or ''}\n\n"
                    f"{st.session_state.final_output.get('draft', '')}"
                ),
                file_name="email_draft.txt",
                mime="text/plain"
            )
        with cols[2]:
            st.button("🧹 Start Over", on_click=reset_conversation)

    else:
        st.markdown("### Conversation")
        st.info("Use the form above to create your first email draft. All versions will remain visible as you revise.")


try:
    run_ui()
except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    traceback.print_exc()
