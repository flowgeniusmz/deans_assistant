# 0. Import Libraries
import streamlit as st
from config import pagesetup as ps, toastalerts as ta
from app import display_title as disTitle, session_states as ss
from openai import OpenAI
import time
from datetime import datetime
import pandas as pd


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
page_subtitle = "Chat History" 
page_icon = "🎓"
page_description = "Allows school administration to view previous chats during the session."
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

## (Set Overview)
ps.set_page_overview(varHeader=overview_header, varText=overview_text)

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
