import streamlit as st
import base64
import pandas as pd

def download_file_link(file_contents, file_name, link_text):
    b64 = base64.b64encode(file_contents.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{file_name}">{link_text}</a>'

