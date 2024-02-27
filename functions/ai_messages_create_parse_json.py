import streamlit as st
from openai import OpenAI

def ai_messages_parse_json(varMessage):
    varMessage_role = varMessage["role"]
    varMessage_content = varMessage["content"]
    return varMessage_role, varMessage_content

def ai_messages_create_json(varRole, varContent):
    varMessage = {
        "role": varRole,
        "content": varContent
    }
    return varMessage