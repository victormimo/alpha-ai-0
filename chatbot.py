import os
import streamlit as st
from llama_index.llms.base import ChatMessage
from llama_index.llms import OpenAI
import openai
from system_prompt import system_prompt
from llama_hub.tools.requests import RequestsToolSpec
from llama_index.agent import OpenAIAgent
from llama_index.chat_engine.types import StreamingAgentChatResponse
from llama_index import SimpleDirectoryReader
from llama_index import Document
from llama_index import VectorStoreIndex
from llama_index import ServiceContext
import datetime
from trulens_eval import (
    Tru,
    Feedback,
    TruLlama,
    OpenAI
)
from trulens_eval.feedback import Groundedness



st.set_page_config(
    page_title="Chat with Alpha AI",
    page_icon="",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)


# Load the OpenAI key from the environment variable
openai_key = os.getenv("OPENAI_KEY")
if not openai_key:
    st.error("No OpenAI key found. Please set the OPENAI_KEY environment variable.")

openai.api_key = openai_key

llm = OpenAI(model="gpt-4", temperature=0.1, system_prompt=system_prompt)



# This function will load the vector store index
@st.cache_data
def load_vector_store_index():
    documents = SimpleDirectoryReader(
        input_files=["./eBook-How-to-Build-a-Career-in-AI.pdf"]
    ).load_data()

    document = Document(text="\n\n".join([doc.text for doc in documents]))

    service_context = ServiceContext.from_defaults(
        llm=llm, embed_model="local:BAAI/bge-small-en-v1.5"
    )
    
    index = VectorStoreIndex.from_documents([document], service_context=service_context)
    return index

index=load_vector_store_index()
query_engine = index.as_query_engine()
print(query_engine)
print("timestamp")
print(datetime.datetime.now())

@st.cache_data
def load_trulens():
    tru = Tru()
    tru.reset_database()

    qa_relevance = (
        Feedback(openai.relevance_with_cot_reasons, name="Answer Relevance")
        .on_input_output()
    )

    qs_relevance = (
        Feedback(openai.relevance_with_cot_reasons, name = "Context Relevance")
        .on_input()
        .on(TruLlama.select_source_nodes().node.text)
        .aggregate(np.mean)
    )

    #grounded = Groundedness(groundedness_provider=openai, summarize_provider=openai)
    grounded = Groundedness(groundedness_provider=openai)

    groundedness = (
        Feedback(grounded.groundedness_measure_with_cot_reasons, name="Groundedness")
            .on(TruLlama.select_source_nodes().node.text)
            .on_output()
            .aggregate(grounded.grounded_statements_aggregator)
    )

    feedbacks = [qa_relevance, qs_relevance, groundedness]

    tru_recorder = TruLlama(
        query_engine,
        app_id="Direct Query Engine",
        feedbacks=feedbacks
        )
    return tru_recorder

# response = query_engine.query(
#     "What are steps to take when finding projects to build your experience?"
# )

# print(str(response))

domain_headers = {
    "api.openai.com": {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json",
    },
    "127.0.0.1": {
        "Content-Type": "application/json",
    },
}



st.title("Alpha AI 0")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello there. How can I help you today?",
        },
    ]



tool_spec = RequestsToolSpec(domain_headers=domain_headers)

agent = OpenAIAgent.from_tools(
    llm=llm,
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
         with tru_recorder as recording:
            # Use query_engine to process the prompt
            vector_response = query_engine.query(prompt)
       

    with st.chat_message("assistant"):
      
        # Display the full response in the chat
        st.markdown(vector_response)

        # Append the response to the session state messages
        st.session_state.messages.append(
            {"role": "assistant", "content": vector_response}
        )


