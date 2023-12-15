import streamlit as st
from config import openai_key, domain_headers
from vector_store import get_vector_store_index
from chat_utils import get_agent, handle_chat_input
from llama_hub.tools.requests import RequestsToolSpec
from llama_index.llms import OpenAI
from system_prompt import system_prompt

# Initialize the Streamlit app configuration
st.set_page_config(
    page_title="Chat with Alpha AI",
    page_icon="",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.title("Alpha AI 0")

print("Loading vector store index...")
# Load the query engine from the vector store index
query_engine = get_vector_store_index()
print("Loaded vector store index. ✅")



res = query_engine.query("What's the best way to get started in AI?")
print("after query engine")
print(str(res))


# Initialize the chat engine and messages history if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello there. How can I help you today?"},
    ]

tool_spec = RequestsToolSpec(domain_headers=domain_headers)

# Initialize the OpenAI agent
llm = OpenAI(model="gpt-4", temperature=0.1, system_prompt=system_prompt)

print("printing llm")
print(llm)

if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = get_agent(llm, tool_spec)

# Initialize the chat messages history if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello there. How can I help you today?"},
    ]

# Chat input
if prompt := st.chat_input(" "):
    st.session_state.messages.append({"role": "user", "content": prompt})
    print("user prompt")
    print(prompt)
    # Process the user prompt with the query engine
    vector_response = query_engine.query(prompt)
    st.session_state.messages.append({"role": "assistant", "content": str(vector_response)})
    
    # Handle the chat response
    chat_responses = handle_chat_input(st.session_state.chat_engine, prompt, st.session_state.messages)
    for chat_response in chat_responses:
        st.session_state.messages.append({"role": "assistant", "content": chat_response})

# Display the conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])