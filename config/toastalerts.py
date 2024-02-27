import streamlit as st

def toast_alert_start(varMessage):
    st.toast(
        body=varMessage,
        icon="⏳"
    )

def toast_alert_end(varMessage):
    st.toast(
        body=varMessage,
        icon="✅"
    )

def toast_alert_waiting(varMessage):
    st.toast(
        body=varMessage,
        icon="⏳"
    )