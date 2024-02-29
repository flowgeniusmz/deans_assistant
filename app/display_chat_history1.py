import streamlit as st
from config import pagesetup as ps

# 1. Function to get St.Session_State.Messages length
def get_message_length():
    message_length = len(st.session_state.messages)
    return message_length

# 2. Function to display chat history if message_length >1
def display_chat_history():
    # filter out runid = 0
    dataframe_messages_filtered = st.session_state.dataframe_messages[st.session_state.dataframe_messages['Run Id'] != '0']

    # group messages df
    dataframe_messages_grouped = dataframe_messages_filtered.groupby('Run Id')

    # iterate over each run
    for run_id, group in dataframe_messages_grouped:
        run_container = st.container(border=True)
        with run_container:
            input_runid = st.text_input(
                label="Run Id",
                value=run_id,
                disabled=True
            )
            #filter for user and assistant
            user_msgs = group[group['Role'] == 'user']['Content']
            assistant_msgs = group[group['Role'] == 'assistant']['Content']

            cc = st.columns(2)
            with cc[0]:
                exp_user = st.expander(label="User Messages", expanded=False)
                with exp_user:
                    for msg in user_msgs:
                        st.markdown(msg)
            with cc[1]:
                exp_asst = st.expander(label="Assistant Messages", expanded=False)
                with exp_asst:
                    for msg in assistant_msgs:
                        st.markdown(msg)

# 3. Function to display error if message length <= 1
def display_no_chat_history():
    
    error_container = st.container(border=False)
    with error_container: 
        error_message = st.error(
            body="**ERROR: No Chat History:** No chat history has been found. Please use the link below to go back to the **Assistant Chat**. Once you start a chat, your chat history will be displayed!",
            icon="⚠️"
        )
        chat_page_link = st.page_link(
            page="pages/1_Assistant_Chat.py",
            label="Click here to go back to **Assistant Chat**",
            icon="💬"
        )

# 4. Function to display error if Manage Assistant tab not visited first
def display_error_chat_history():
    warning_container = st.container(border=False)
    with warning_container: 
        warning_message = st.warning(
            body="**ERROR: Chat History Not Displayed:** You must first go to **Manage Assistant** page first before any chat history will be displayed. Please use the link below to go to **Manage Assistant** and then return back to **Chat History**. (Note: This is a temporary bug that will be resolved)",
            icon="⚠️"
        )
        manage_page_link = st.page_link(
            page="pages/2_Manage_Assistant.py",
            label="Click here to go back to **Manage Assistant**",
            icon="💬"
        )

# 5. Display Function for Chat History
def chat_history_display():
    msg_len = get_message_length()
    if msg_len <= 1:
        display_no_chat_history()
    else:
        display_chat_history()

