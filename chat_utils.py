from llama_index.llms.base import ChatMessage
from llama_index.agent import OpenAIAgent
from llama_index.chat_engine.types import StreamingAgentChatResponse
import streamlit as st

def get_agent(llm, tool_spec):
    return OpenAIAgent.from_tools(
        llm=llm,
        tools=tool_spec.to_tool_list(),
        system_prompt=system_prompt,
    )

def handle_chat_input(agent, prompt, session_state_messages):
    responses = []
    if prompt:
        with st.spinner("The AI is thinking..."):
            chat_response: StreamingAgentChatResponse = agent.stream_chat(
                prompt,
                [ChatMessage(role=m["role"], content=m["content"]) for m in session_state_messages],
            )
            # Process the response
            while not chat_response._is_done and chat_response._queue.empty():
                continue
            for response_chunk in chat_response.response_gen:
                responses.append(response_chunk)
    return responses
