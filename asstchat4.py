# Import Libraries
import streamlit as st
from config import pagesetup as ps, toastalerts as ta
from app import display_title as disTitle, session_states as ss
from openai import OpenAI
import time
from datetime import datetime
from typing import List, Dict, Any
import base64

# Constants
ASSISTANT_AVATAR = "assets/images/logo/icon.png"
USER_AVATAR = "assets/images/logo/school.png"

# Initialize Session State
if "start_chat" not in st.session_state:
    ss.get_initial_session_states()

# Initialize OpenAI Client
client = OpenAI(api_key=st.secrets.openai.api_key)

# Page Configuration
st.set_page_config(
    page_title="Dean's Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Display Page Title
disTitle.display_title_section(
    varTitle="Dean's Assistant",
    varSubtitle="AI Assistant"
)

def display_existing_messages(chat_container: st.container):
    """Display existing chat messages from session state."""
    for message in st.session_state.messages:
        avatar = ASSISTANT_AVATAR if message["role"] == "assistant" else USER_AVATAR
        with chat_container.chat_message(name=message["role"], avatar=avatar):
            if message["role"] == "assistant":
                display_assistant_message(message["content"])
            else:
                st.markdown(message["content"])

@st.cache_data(show_spinner=False)
def retrieve_file(file_id: str) -> bytes:
    """Retrieve file content from OpenAI."""
    file = client.files.retrieve(file_id)
    return file.content  # Assuming 'content' contains the file bytes

def display_assistant_message(content: str):
    """Display assistant message with optional citations."""
    st.markdown(content)
    # Extract citations if present
    if "**Citations:**" in content:
        citations_section = content.split("**Citations:**")[1].strip()
        citations = citations_section.split("\n")
        if citations:
            st.markdown("**Citations:**")
            for citation in citations:
                if "Click <here> to download" in citation:
                    filename = citation.split("download ")[1]
                    file_id = extract_file_id(citation)  # Implement this based on your citation format
                    file_content = retrieve_file(file_id)
                    st.download_button(
                        label=f"Download {filename}",
                        data=file_content,
                        file_name=filename,
                        mime="application/octet-stream"
                    )
                else:
                    st.markdown(citation)

def extract_file_id(citation: str) -> str:
    """
    Extract file ID from citation string.
    This function needs to be implemented based on how file IDs are represented in citations.
    """
    # Example implementation (modify according to actual citation format)
    # Assuming citation format: "[index] Click <here> to download filename (file_id)"
    try:
        file_id = citation.split("(")[1].rstrip(")")
        return file_id
    except IndexError:
        return ""

def process_assistant_messages(run_id: str) -> List[Dict[str, Any]]:
    """Retrieve and process assistant messages from OpenAI."""
    thread_messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    new_messages = []

    for thread_message in thread_messages:
        if thread_message.run_id == run_id and thread_message.role == "assistant":
            content = thread_message.content[0].text
            annotations = content.annotations
            citations = []
            content_value = content.value
            content_display = content_value

            for index, annotation in enumerate(annotations):
                placeholder = f' [{index}]'
                content_display = content_display.replace(annotation.text, placeholder)

                if hasattr(annotation, 'file_citation'):
                    file_id = annotation.file_citation.file_id
                    file = client.files.retrieve(file_id)
                    citations.append(f'[{index}] Citation from {file.filename} (ID: {file_id})')
                elif hasattr(annotation, 'file_path'):
                    file_id = annotation.file_path.file_id
                    file = client.files.retrieve(file_id)
                    citations.append(f'[{index}] Click <here> to download {file.filename} (ID: {file_id})')

            # Only add citations header if there are citations
            if citations:
                content_display += '\n\n**Citations:**\n' + '\n'.join(citations)

            message = {
                "role": thread_message.role,
                "content": content_display,
                "messageid": thread_message.id,
                "runid": thread_message.run_id,
                "createdatunix": thread_message.created_at,
                "createdatdatetime": datetime.utcfromtimestamp(thread_message.created_at)
            }
            new_messages.append(message)

    return new_messages

def handle_user_prompt(prompt: str, chat_container: st.container):
    """Handle the user's prompt and display the assistant's response."""
    ta.toast_alert_start("Getting response...")
    prompt_role = "user"
    new_message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        content=prompt,
        role=prompt_role
    )

    # Display user message
    with chat_container.chat_message(name=prompt_role, avatar=USER_AVATAR):
        st.markdown(prompt)

    # Display running status
    with chat_container:
        status = st.status(
            label="Initiating response...",
            expanded=False,
            state="running"
        )

    # Initiate run with instructions
    st.session_state.run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.secrets.openai.assistant_id,
        instructions=st.session_state.run_instructions
    )

    # Update session state with user message
    prompt_message = {
        "role": prompt_role,
        "content": prompt,
        "messageid": new_message.id,
        "runid": st.session_state.run.id,
        "createdatunix": new_message.created_at,
        "createdatdatetime": datetime.utcfromtimestamp(new_message.created_at)
    }
    st.session_state.messages.append(prompt_message)

    # Wait for run to complete
    while st.session_state.run.status != "completed":
        time.sleep(3)
        ta.toast_alert_waiting("Awaiting response...")
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=st.session_state.run.id
        )
        with chat_container:
            status.write(f"Checking response status... {st.session_state.run.status}")

    # Update status to complete
    with chat_container:
        status.update(
            label="Response received!",
            expanded=False,
            state="complete"
        )
        ta.toast_alert_end("Response received!")

    # Retrieve and process assistant messages
    new_assistant_messages = process_assistant_messages(st.session_state.run.id)
    for message in new_assistant_messages:
        st.session_state.messages.append(message)
        with chat_container.chat_message(name="assistant", avatar=ASSISTANT_AVATAR):
            display_assistant_message(message["content"])

def main():
    """Main function to run the Streamlit app."""
    chat_container = st.container()
    with chat_container:
        display_existing_messages(chat_container)

    # Chat Input for the user
    prompt = st.chat_input("Enter your question (Ex: A student has their third tardy. What consequences should be considered?)")
    if prompt:
        handle_user_prompt(prompt, chat_container)

main()
