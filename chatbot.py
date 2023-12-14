import os
import streamlit as st
from llama_index.llms.base import ChatMessage
from llama_index.llms import OpenAI
import openai
from system_prompt import system_prompt
from llama_hub.tools.requests import RequestsToolSpec
from llama_index.agent import OpenAIAgent
from llama_index.chat_engine.types import StreamingAgentChatResponse

openai_key = os.getenv("OPENAI_KEY")
if not openai_key:
    st.error("No OpenAI key found. Please set the OPENAI_KEY environment variable.")

domain_headers = {
    "api.openai.com": {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json",
    },
    "127.0.0.1": {
        "Content-Type": "application/json",
    },
}

st.set_page_config(
    page_title="Chat with Alpha AI",
    page_icon="",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

openai.api_key = openai_key
st.title("Alpha AI")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello there.",
        },
        {
            "role": "assistant",
            "content": "How are you?",
        },
    ]


# @ st.cache_resource(show_spinner=False)
# def load_data():
#     with st.spinner(text=""):
#         reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
#         docs = reader.load_data()
#         service_context = ServiceContext.from_defaults(llm=OpenAI(
#             model="gpt-4", temperature=0.5, system_prompt=system_prompt))
#         index = VectorStoreIndex.from_documents(
#             docs, service_context=service_context)
#         return index

# index = load_data()
# chat_engine = index.as_chat_engine( chat_mode="condense_question", verbose=True, system_prompt=system_prompt)

tool_spec = RequestsToolSpec(domain_headers=domain_headers)
agent = OpenAIAgent.from_tools(
    llm=OpenAI(model="gpt-4", temperature=0, system_prompt=system_prompt),
    tools=tool_spec.to_tool_list(),
    system_prompt=system_prompt,
)

if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.chat_engine: OpenAIAgent = agent
if prompt := st.chat_input(" "):
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.spinner("The AI is thinking..."):
        response: StreamingAgentChatResponse = st.session_state.chat_engine.stream_chat(
            prompt,
            [
                ChatMessage(role=m["role"], content=m["content"])
                for m in st.session_state.messages
            ],
        )
        # while there processing and no response, keep showing the spinner
        while not response._is_done and response._queue.empty():
            continue

    with st.chat_message("assistant"):
        full_response = ""
        message_placeholder = st.empty()
        for response_chunk in response.response_gen:
            # Update the full response and the placeholder with the received chunk
            full_response += response_chunk
            message_placeholder.markdown(full_response + "▌")

        # Update the placeholder with the final response
        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
