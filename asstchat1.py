# Import Libraries
import streamlit as st
from config import pagesetup as ps, toastalerts as ta
from app import display_title as disTitle, session_states as ss
from openai import OpenAI
import time
from datetime import datetime

if "start_chat" not in st.session_state:
    ss.get_initial_session_states()

# Set Instances
client = OpenAI(api_key=st.secrets.openai.api_key)

# Page Setup
app_name = "Dean's Assistant"
app_layout = "wide"
app_sidebar = "collapsed"
page_title = "Dean's Assistant"
page_subtitle = "AI Assistant" 
page_icon = "🎓"
page_description = "Allows school administration to interact with their custom AI assistant."
overview_header = "Overview"
overview_text = f"**{page_subtitle}** {page_description.lower()}"

# Set Page Config
st.set_page_config(
    page_title=app_name,
    page_icon=page_icon,
    layout=app_layout,
    initial_sidebar_state=app_sidebar
)

# Set Page Title
disTitle.display_title_section(
    varTitle=page_title,
    varSubtitle=page_subtitle
)


# Display Existing Messages in the chat
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        message_role = message["role"]
        if message_role == "assistant":
            avatarpath = "assets/images/logo/icon.png"
            
        elif message_role == "user":
            avatarpath = "assets/images/logo/school.png"
            

        message_content = message["content"]
        with st.chat_message(name=message_role, avatar=avatarpath):
            st.markdown(message_content)

# Chat Input for the user
if prompt := st.chat_input("Enter your question (Ex: A student has their third tardy. What consequences should be considered?)"):
    ta.toast_alert_start("Getting response...")
    # add to st.session_state.messages
    prompt_role = "user"
    prompt_content = prompt
    new_message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        content=prompt_content,
        role=prompt_role
    )

    with chat_container:
        with st.chat_message(name=prompt_role, avatar="assets/images/logo/school.png"):
            st.markdown(prompt_content)
    
    with chat_container:
        status = st.status(
        label="Initiating response...",
        expanded=False,
        state="running"
        )
    
    # Initiate a run with additional instructions
    st.session_state.run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.secrets.openai.assistant_id,
        instructions=st.session_state.run_instructions
    )

    # Add to session state
    prompt_message = {"role": prompt_role, "content": prompt_content, "messageid": new_message.id, "runid": st.session_state.run.id, "createdatunix": new_message.created_at, "createdatdatetime": datetime.utcfromtimestamp(new_message.created_at)}
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
            status.write(f"Checking response status...{st.session_state.run.status}")

    with chat_container:
        status.update(
            label="Response recieved!",
            expanded=False,
            state="complete"
        )

        ta.toast_alert_end("Response received!")
    
    # Retrieve messages added by assistant
    thread_messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    # Get assistant new messages
    for thread_message in thread_messages:
        thread_message_run_id = thread_message.run_id
        thread_message_role = thread_message.role
        if thread_message_run_id == st.session_state.run.id and thread_message_role == "assistant":
            thread_message_id = thread_message.id
            thread_message_unix = thread_message.created_at
            thread_message_datetime = datetime.now()
            thread_message_text = thread_message.content[0].text
            thread_message_annotations = thread_message_text.annotations
            citations = []
            thread_message_content = thread_message.content[0].text.value
            thread_message_content_replace = thread_message_content

            for index, annotation in enumerate(thread_message_annotations):
                thread_message_content_replace = thread_message_content_replace.replace(annotation.text, f' [{index}]')
                if hasattr(annotation, 'file_citation'):
                    file_citation = annotation.file_citation
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(f'[{index}] Citation from {cited_file.filename}')
                elif hasattr(annotation, 'file_path'):
                    file_path = annotation.file_path
                    cited_file = client.files.retrieve(file_path.file_id)
                    citations.append(f'[{index}] Click <here> to download {cited_file.filename}')

            thread_message_content_replace += '\n\n**Citations:**\n' + '\n'.join(citations)
            
            add_thread_message = {"role": thread_message_role, "content": thread_message_content_replace, "messageid": thread_message_id, "runid": thread_message_run_id, "createdatunix": thread_message_unix, "createdatdatetime": thread_message_datetime}
            st.session_state.messages.append(add_thread_message)

            with chat_container:
                with st.chat_message(name="assistant", avatar="assets/images/logo/icon.png"):
                    st.markdown(thread_message_content_replace)
