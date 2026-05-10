# Email Copilot

A Streamlit-based email drafting assistant that uses LangGraph and OpenAI to generate, personalize, and revise professional emails through a multi-stage agent workflow.

## High Level Architecture

- `src/ui/app.py`
  - Streamlit UI for composing email briefs, viewing chat history, and applying revision feedback.
  - Calls a reusable workflow app compiled from `src.workflow`.
- `src/workflow/graph.py`
  - Builds and compiles the LangGraph state graph for the email assistant.
  - Defines agent nodes and transitions, including review-based looping.
- `src/agents/`
  - Contains individual agent modules that perform parsing, intent detection, tone styling, personalization, draft generation, and review routing.
  - `src/agents/state.py` defines the shared typed state shape used across the pipeline.
- `main.py`
  - Example entry point to compile the workflow and run a sample email generation.

## Requirements

- Python 3.10+ (recommended)
- `OPENAI_API_KEY` configured in an environment variable or `.env` file
- `streamlit` for the web UI
- LangGraph and OpenAI-compatible dependencies installed in the project environment

## Setup Instructions

1. Clone the repository:

   ```powershell
   git clone <repo-url> ik_email_asst
   cd ik_email_asst
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create a `.env` file at the project root with your OpenAI key:

   ```text
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. Run the Streamlit app:

   ```powershell
   streamlit run .\src\ui\app.py
   ```

## Usage

- Open the app URL shown by Streamlit.
- Enter recipient, subject, tone, and an email brief.
- Generate the draft and optionally provide revision feedback.
- Continue refining until the email meets your needs.
- Download the latest draft using the download button.

## Notes

- The workflow is cached with Streamlit's `@st.cache_resource` decorator for faster reuse during a session.
- Revision feedback loops back through the draft writer when review determines the email is not valid.
- `src/agents/state.py` is the single typed source of truth for the agent pipeline state.

## Project Structure

- `src/agents/`
  - `input_parser_agent.py`
  - `intent_detection_agent.py`
  - `tone_stylist_agent.py`
  - `personalization_agent.py`
  - `draft_writer_agent.py`
  - `review_agent.py`
  - `router_agent.py`
  - `state.py`
- `src/ui/app.py`
- `src/workflow/graph.py`
- `main.py`
- `requirements.txt`

## Troubleshooting

- If the app fails to start, verify `OPENAI_API_KEY` is set and valid.
- If imports fail, ensure the virtual environment is activated and dependencies installed.
- For Streamlit UI issues, restart the app after changing code or `.env` values.
