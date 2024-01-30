import os
import datetime
from dotenv import load_dotenv
import sys
import streamlit as st
from llama_index.llms import OpenAI as LlamaOpenAI
import openai 
from system_prompt import system_prompt
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.agent import OpenAIAgent
from llama_index import SimpleDirectoryReader
from llama_index import Document
import logging
import sys

sys.path.append("utils")

# importing utils
from sentence_window_retrieval import build_sentence_window_index, get_sentence_window_query_engine
from automerging_retrieval import build_automerging_index, get_automerging_query_engine

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

load_dotenv()

st.set_page_config(
    page_title="Chat with Alpha AI",
    page_icon="",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

# Load the OpenAI key from the environment variable
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    st.error("No OpenAI key found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = openai_key

llm = LlamaOpenAI(model="gpt-4-0125-preview", temperature=0.1, system_prompt=system_prompt)

@st.cache_data
def load_data():
    print("loading documents")

    documents_ivey = SimpleDirectoryReader(input_dir="./data/ivey/", required_exts=[".txt"], recursive=True).load_data()
    documents_queens = SimpleDirectoryReader(input_dir="./data/queens/", required_exts=[".txt"], recursive=True).load_data()

    return documents_ivey, documents_queens

documents_ivey, documents_queens  = load_data()

@st.cache_resource
def load_automerging_retrieval_ivey():
    print("loading automerging retrieval ivey")
    automerging_index = build_automerging_index(
        documents_ivey,
        llm,
        embed_model="local:BAAI/bge-small-en-v1.5",
        save_dir="merging_index"
    )
    automerging_engine = get_automerging_query_engine(automerging_index)
    return automerging_engine

@st.cache_resource
def load_automerging_retrieval_queens():
    print("loading automerging retrieval queens")
    automerging_index = build_automerging_index(
        documents_queens,
        llm,
        embed_model="local:BAAI/bge-small-en-v1.5",
        save_dir="merging_index"
    )
    automerging_engine = get_automerging_query_engine(automerging_index)
    return automerging_engine


query_engine_ivey = load_automerging_retrieval_ivey() 
query_engine_queens = load_automerging_retrieval_queens()


# Load the tools
query_tools = [
    QueryEngineTool(
        query_engine=query_engine_ivey,
        metadata = ToolMetadata(
            name="ivey_automerging_qe",
            description="Ivey Query Engine",
        )
    ),
    QueryEngineTool(
        query_engine=query_engine_queens,
        metadata = ToolMetadata(
            name="queens_automerging_qe",
            description="Queens Query Engine",
        )
    )
]

agent = OpenAIAgent.from_tools(
    llm=llm,
    tools=query_tools,
    verbose=True,
    system_prompt=system_prompt,
)

# CHAT 

st.title("Alpha AI 0")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello there. How can I help you today?",
        },
    ]

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
        # Use query_engine to process the prompt
        vector_response = st.session_state.chat_engine.chat(prompt)
       

    with st.chat_message("assistant"):
        response_string = vector_response.response
        
        # Display the full response in the chat
        st.markdown(response_string)

        # Append the response to the session state messages
        st.session_state.messages.append(
            {"role": "assistant", "content": response_string}
        )


