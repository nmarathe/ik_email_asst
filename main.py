import os
from src.workflow import compile_graph


def run_sample():
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("❌ OPENAI_API_KEY is missing from the environment or .env file.")

    app = compile_graph()
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
