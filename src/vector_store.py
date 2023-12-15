import streamlit as st
from llama_index import SimpleDirectoryReader, Document, VectorStoreIndex, ServiceContext
from llama_index.llms import OpenAI
from system_prompt import system_prompt

llm = OpenAI(model="gpt-4", temperature=0.1, system_prompt=system_prompt)

# @st.cache_data
def get_vector_store_index():
    documents = SimpleDirectoryReader(
        input_files=["./eBook-How-to-Build-a-Career-in-AI.pdf"]
    ).load_data()
    document = Document(text="\n\n".join([doc.text for doc in documents]))
   
    service_context = ServiceContext.from_defaults(
        llm=llm, embed_model="local:BAAI/bge-small-en-v1.5"
    )
    index = VectorStoreIndex.from_documents([document], service_context=service_context)
    return index.as_query_engine()
