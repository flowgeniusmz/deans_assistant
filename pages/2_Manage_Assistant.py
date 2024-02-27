# 0. Import Libraries
import streamlit as st
from config import pagesetup as ps
from app import display_title as disTitle
from openai import OpenAI
import pandas as pd

# Set Instances
client = OpenAI(api_key=st.secrets.openai.api_key)
df_files = pd.DataFrame(
    columns=["File Id", "Object Type", "Created At", "Assistant Id"]
)
df_tools = pd.DataFrame(
    columns=["Type"]
)

# 1. Page Setup
## (Page Information)
app_name = "Dean's Assistant"
app_layout = "wide"
app_sidebar = "collapsed"
page_title = "Dean's Assistant"
page_subtitle = "Manage Assistant" 
page_icon = "🎓"
page_description = "Allows school administration to manage details about the assistant."
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

# 2. Display
main_container = st.container(border=True)
with main_container:
    details_container = st.container()
    with details_container:
        cc_details = st.columns(3)
        with cc_details[0]:
            asst_name = st.text_input(
                label="Assistant Name",
                value=st.session_state.assistant_name,
                disabled=True
            )
        with cc_details[1]:
            asst_model = st.text_input(
                label="Assistant Model",
                value=st.session_state.assistant_model,
                disabled=True
            )
        with cc_details[2]:
            asst_desc = st.text_input(
                label="Assistant Description",
                value=st.session_state.assistant_description,
                disabled=True
            )
        asst_inst = st.text_area(
            label="Assistant Instructions", 
            value=st.session_state.assistant_instructions,
            disabled=True,
            height=400 
        )
    tabs_container = st.container(border=True)
    with tabs_container:
        tab_names = ['Files', 'Tools']
        tab1, tab2 = st.tabs(tab_names)
        with tab1:
            for file_id in st.session_state.assistant_file_ids:
                file_object = client.beta.assistants.files.retrieve(
                    file_id=file_id,
                    assistant_id=st.session_state.assistant.id
                )
                new_row_files = {
                    "File Id": file_object.id,
                    "Object Type": file_object.object,
                    "Created At": file_object.created_at,
                    "Assistant Id": file_object.assistant_id
                }
                df_files = df_files._append(new_row_files, ignore_index=True)
            st.dataframe(df_files, use_container_width=True)
        with tab2:
            for tool in st.session_state.assistant_tools:
                new_row_tools = {
                    "Type": tool.type
                }
                df_tools = df_tools._append(new_row_tools, ignore_index=True)
            st.dataframe(df_tools, use_container_width=True)