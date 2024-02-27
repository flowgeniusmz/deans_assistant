import streamlit as st
import uuid
from openai import OpenAI


def get_initial_session_states():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "school_name" not in st.session_state:
        st.session_state.school_name = "John F Kennedy Middle School"
        st.session_state.initial_message = {"role": "assistant", "content": f"Welcome to {st.session_state.school_name}! I am your AI assistant - how may I help you?"}
    if "openai_client" not in st.session_state:
        st.session_state.openai_client = OpenAI(api_key=st.secrets.openai.api_key)
        st.session_state.openai_model = st.secrets.openai.model_gpt4_preview
    if "assistant" not in st.session_state:
        st.session_state.assistant = st.session_state.openai_client.beta.assistants.retrieve(assistant_id=st.secrets.openai.assistant_id)
        st.session_state.assistant_instructions = st.session_state.assistant.instructions
        st.session_state.assistant_file_ids = st.session_state.assistant.file_ids
        st.session_state.assistant_tools = st.session_state.assistant.tools
        st.session_state.assistant_model = st.session_state.assistant.model
        st.session_state.assistant_name = st.session_state.assistant.name
        st.session_state.assistant_description = st.session_state.assistant.description
    if "thread" not in st.session_state:
        st.session_state.thread = st.session_state.openai_client.beta.threads.create(
            metadata={'session_id': st.session_state.session_id,}
        )
        st.session_state.thread_id = st.session_state.thread.id
    if "start_chat" not in st.session_state:
        st.session_state.start_chat = True
    if "file_id_list" not in st.session_state:
        st.session_state.file_id_list = []
    if "ignore_file_ids" not in st.session_state:
        st.session_state.ignore_file_ids = True
    if "run" not in st.session_state:
        st.session_state.run = {"status": None}
        st.session_state.run_instructions = "Please answer the query or input using the instructions and files you have been given. If you cant find the appropriate information, say you don't know. Always include citations where possible."
    if "messages" not in st.session_state:
        st.session_state.messages = [st.session_state.initial_message]
    if "retry_error" not in st.session_state:
        st.session_state.retry_error = 0
