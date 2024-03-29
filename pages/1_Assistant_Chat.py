# 0. Import Libraries
import streamlit as st
from config import pagesetup as ps, toastalerts as ta
from app import display_title as disTitle, session_states as ss
from openai import OpenAI
import time
from datetime import datetime

if "start_chat" not in st.session_state:
    ss.get_initial_session_states()

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
#ps.set_page_overview(
#    varHeader=overview_header,
#    varText=overview_text
#)

##########################################################################
# Instructions
# - Create a container for the chat messages using border and fixed height
# - Need to display existing messages in st.session_state.messages using "With St.Chat_Message(Role): st.Markdown(content)"
# - Next is input - outside of the chat container
#
#
#
# 2. Display Existing Messages in teh chat
chat_container = st.container(border=True, height=450)
with chat_container:
    for message in st.session_state.messages:
        message_role = message["role"]
        message_content = message["content"]
        with st.chat_message(message_role):
            st.markdown(message_content)

# 3. Chat Input for the user
if prompt := st.chat_input("Enter your question (Ex: A student has their third tardy. What consequences should be considered?)", ):
    ta.toast_alert_start("Getting response...")
    # add to st.session_state.messages
    prompt_role = "user"
    prompt_content = prompt
    new_message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        content=prompt_content,
        role=prompt_role
    )
    #prompt_message = {"role": prompt_role, "content": prompt_content, "messageid": new_message.id}
    #st.session_state.messages.append(prompt_message)
    # display message
    with chat_container:
        with st.chat_message(prompt_role):
            st.markdown(prompt_content)
    #add message to existing thread
    #new_message = client.beta.threads.messages.create(
    #    thread_id=st.session_state.thread_id,
    #    content=prompt_content,
    #    role=prompt_role
    #)
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
    ta.toast_alert_end("Response recieved!")
    # retrieve messages added by assistant
    thread_messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    # get assistant new messages
    for thread_message in thread_messages:
        thread_message_run_id = thread_message.run_id
        thread_message_role = thread_message.role
        if thread_message_run_id == st.session_state.run.id and thread_message_role == "assistant":
            thread_message_id = thread_message.id
            thread_message_unix = thread_message.created_at
            thread_message_datetime = datetime.utcfromtimestamp(thread_message_unix)
            thread_message_text = thread_message.content[0].text
            thread_message_annotations = thread_message_text.annotations
            citations=[]
            thread_message_content = thread_message.content[0].text.value
            thread_message_content_replace = thread_message_content
            for index, annotation in enumerate(thread_message_annotations):
                thread_message_content_replace = thread_message_content_replace.replace(annotation.text, f' [{index}]')
                if (file_citation:=getattr(annotation, 'file_citation', None)):
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
                elif (file_path := getattr(annotation, 'file_path', None)):
                    cited_file = client.files.retrieve(file_path.file_id)
                    citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
            thread_message_content_replace += '\n' + '\n\n' + '**Citations:**' + '\n' + '\n'.join(citations)
            print(thread_message_content)
            print(thread_message_content_replace)
            #print(thread_message_content_replace)
            add_thread_message = {"role": thread_message_role, "content": thread_message_content_replace, "messageid": thread_message_id, "runid": thread_message_run_id, "createdatunix": thread_message_unix, "createdatdatetime": thread_message_datetime}
            st.session_state.messages.append(add_thread_message)
            with chat_container:
                #with st.chat_message(thread_message_role):
                #    st.markdown(thread_message_content)
                with st.chat_message("assistant"):
                    st.markdown(thread_message_content_replace)