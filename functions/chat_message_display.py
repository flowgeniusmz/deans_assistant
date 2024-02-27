import streamlit as st

def display_chat_message(varRole, varContent):
    with st.chat_message(varRole):
        st.markdown(varContent)