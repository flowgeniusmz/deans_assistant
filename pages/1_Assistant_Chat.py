# 0. Import Libraries
import streamlit as st
from config import pagesetup as ps
from app import display_title as disTitle
from openai import OpenAI
import time

# 0. Set Instances
client = OpenAI(api_key=st.secrets.openai.api_key)

# 1. Page Setup
## (Page Information)
app_name = "Dean's Assistant"
app_layout = "wide"
app_sidebar = "collapsed"
page_title = "Dean's Assistant"
page_subtitle = "AI Assistant" 
page_icon = "🎓"
page_description = "Allows school administration to interact with their custom AI assistant."
overview_header = "Overview"
overview_text = f"**{page_subtitle}** {page_description.lower()}"

## (Set Page Config)
st.set_page_config(
    page_title=app_name,
    page_icon=page_icon,
    layout=app_layout,
    initial_sidebar_state=app_sidebar
)

## (Set Page Title)
disTitle.display_title_section(
    varTitle=page_title,
    varSubtitle=page_subtitle
)

## (Set Page Overview)
ps.set_page_overview(
    varHeader=overview_header,
    varText=overview_text
)


# 2. Display Existing Messages in teh chat
chat_container = st.container(border=True, height=300)
with chat_container:
    for message in st.session_state.messages:
        message_role = message["role"]
        message_content = message["content"]
        with st.chat_message(message_role):
            st.markdown(message_content)

# 3. Chat Input for the user
if prompt := st.chat_input("Enter your question (Ex: A student has their third tardy. What consequences should be considered?)"):
    # add to st.session_state.messages
    prompt_role = "user"
    prompt_content = prompt
    prompt_message = {"role": prompt_role, "content": prompt_content}
    st.session_state.messages.append(prompt_message)
    # display message
    with chat_container:
        with st.chat_message(prompt_role):
            st.markdown(prompt_content)
    #add message to existing thread
    new_message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        content=prompt_content,
        role=prompt_role
    )
    with chat_container:
        status = st.status(
            label="Initiating response...",
            expanded=False,
            state="running"
        )
    # Create a run with additional instructions
    st.session_state.run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.secrets.openai.assistant_id,
        instructions=st.session_state.run_instructions
    )

    # Wait for run to complete
    while st.session_state.run.status != "completed":
        time.sleep(1)
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
    # retrieve messages added by assistant
    thread_messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    # get assistant new messages
    for thread_message in thread_messages:
        thread_message_run_id = thread_message.run_id
        thread_message_role = thread_message.role
        if thread_message_run_id == st.session_state.run.id and thread_message_role == "assistant":
            thread_message_content = thread_message.content[0].text.value
            add_thread_message = {"role": thread_message_role, "content": thread_message_content}
            st.session_state.messages.append(add_thread_message)
            with chat_container:
                with st.chat_message(thread_message_role):
                    st.markdown(thread_message_content)