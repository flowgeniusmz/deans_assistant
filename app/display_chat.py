import streamlit as st
from openai import OpenAI
from config import toastalerts as ta
import time

client = OpenAI(api_key=st.secrets.openai.api_key)

def display_ai_chat():
    # 0. Set Chat Container
    chat_message_container = st.container(
        height=400,
        border=True
    )
    # 1. Set chat input (NOTE: Streamlit reads top to bottom soit will set this outside the container - can comment out if prefer to use prompt:=)
    chat_input = st.chat_input(
        placeholder="Enter your question here! (Ex: A student has three tardies. What should the consequences be?)"
    )
    # 2. Display current messages in st.session_state
    with chat_message_container:
        for existing_message in st.session_state.messages:
            existing_message_role = existing_message["role"]
            existing_message_content = existing_message["content"]
            with st.chat_message(existing_message_role):
                st.markdown(existing_message_content)
    # 3. Await user input and initiate actions (session state)
    if chat_input:
        user_message_role = "user"
        user_message_content = "chat_input"
        user_message = {
            "role": user_message_role,
            "content": user_message_content
        }
        st.session_state.messages.append(user_message)
    # 4. Display user input message
        with chat_message_container:
            with st.chat_message(user_message_role):
                st.markdown(user_message_content)
    # 5. Create thread message
        new_thread_message = client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role=user_message_role,
            content=user_message_content
        )
    # 6. Initializing response messages
        ta.toast_alert_start("Initializing response...")
        with chat_message_container:
            status_box = st.status(
                label="Initializing response...",
                expanded=False,
                state="running"
            )
            status_box.write("Initializing response...")
    # 7. Starting Run
        st.session_state.run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant.id,
            additional_instructions=st.session_state.run_instructions
        )
    # 8. Check Run
        while st.session_state.run.status != "completed":
            time.sleep(2)
    # 9. In progress messages
            ta.toast_alert_waiting("Awaiting response...")
            with chat_message_container:
                status_box.update(
                    label="Awaiting response...",
                    expanded=False,
                    state="running"
                )
                status_box.write(f"Awaiting response...{st.session_state.run.status}")
    # 10. Complete - Messages FIRST
        ta.toast_alert_end("Response recieved!")
        with chat_message_container:
            status_box.update(
                label="Reponse recieved!",
                expanded=False,
                state="complete"
            )
            status_box.write("Response recieved")
    # 11. Complete - Get Thread Message
        thread_message_list = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
    # 12. Break apart thread messages
        for thread_message in thread_message_list:
            thread_message_runid = thread_message.run_id
            thread_message_role = thread_message.role
            if thread_message_runid == st.session_state.run.id and thread_message_role == "assistant":
                thread_message_content_value = thread_message.content[0].text.value
    # 13. Add to session state messages
                add_thread_message = {
                    "role": thread_message_role,
                    "content": thread_message_content_value
                }
                st.session_state.messages.append(add_thread_message)
    # 14. Display new message
                with chat_message_container:
                    with st.chat_message(thread_message_role):
                        st.markdown(thread_message_content_value)
