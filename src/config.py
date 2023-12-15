import os

# Load the OpenAI key from the environment variable
openai_key = os.getenv("OPENAI_KEY")

if not openai_key:
    raise ValueError("No OpenAI key found. Please set the OPENAI_KEY environment variable.")

domain_headers = {
    "api.openai.com": {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json",
    },
    "127.0.0.1": {
        "Content-Type": "application/json",
    },
}
