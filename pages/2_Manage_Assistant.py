# 0. Import Libraries
import streamlit as st
from config import pagesetup as ps
from app import display_title as disTitle
from openai import OpenAI
import pandas as pd
import base64
from datetime import datetime
import time
import csv

# Set Instances
client = OpenAI(api_key=st.secrets.openai.api_key)
df_files = pd.DataFrame(
    columns=["File Id", "Object Type", "Created At", "Assistant Id"]
)
df_files1 = pd.DataFrame(
    columns=["Id", "Object", "Bytes", "Created At", "Name", "Purpose", "Download Link"]
)
df_tools = pd.DataFrame(
    columns=["Type"]
)
df_messages = pd.DataFrame(
    columns=["Role", "Content", "Thread Id", "Message Id", "Run Id", "Session Id", "Created At Unix", "Created At Datetime"]
)

def download_file_link(file_contents, file_name, link_text):
    b64 = base64.b64encode(file_contents.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{file_name}">{link_text}</a>'


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
    with stylable_container(
        key="container_with_border",
        css_styles="""
            {
                border: 1px solid rgba(11, 140, 71, 0.62);
                border-radius: 0.5rem;
                padding: calc(1em - 1px)
            }
            """,
        ):
            ps.set_blue_header(varSubtitle="Basic Information")
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
    ps.set_blue_header(varSubtitle="Details and Actions")
    tabs_container = st.container(border=True)
    with tabs_container:
        tab_names = ['Files', 'Tools', 'File Download', 'Message Log', 'Add Assistant File']
        tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_names)
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
                st.session_state.dataframe_files = st.session_state.dataframe_files._append(new_row_files, ignore_index=True)
            st.dataframe(df_files, use_container_width=True)
        with tab2:
            for tool in st.session_state.assistant_tools:
                new_row_tools = {
                    "Type": tool.type
                }
                df_tools = df_tools._append(new_row_tools, ignore_index=True)
                st.session_state.dataframe_tools = st.session_state.dataframe_tools._append(new_row_tools, ignore_index=True)
            st.dataframe(df_tools, use_container_width=True)
        with tab3:
            for file_id in st.session_state.assistant_file_ids:
                file_object1 = client.files.retrieve(
                    file_id=file_id
                )
                #file_contents = client.files.content(
                    #file_id=file_id
                #)
                #file_link = download_file_link(
                #    file_contents=file_contents,
                #    file_name=file_object1.filename,
                #    link_text="Download Link"
                #)
                new_row_files1 = {
                    "Id": file_object1.id,
                    "Object": file_object1.object,
                    "Bytes": file_object1.bytes,
                    "Created At": file_object1.created_at,
                    "Name": file_object1.filename ,
                    "Purpose": file_object1.purpose,
                    #"Download Link": file_link
                }
                df_files1 = df_files1._append(new_row_files1, ignore_index=True)
                st.session_state.dataframe_files1 = st.session_state.dataframe_files1._append(new_row_files1, ignore_index=True)
            st.dataframe(df_files1, use_container_width=True)
        with tab4:
            for msg in st.session_state.messages:
                new_row_messages = {
                    "Role": msg['role'],
                    "Content": msg['content'],
                    "Thread Id": st.session_state.thread_id,
                    "Message Id": msg['messageid'],
                    "Run Id": msg['runid'],
                    "Session Id": st.session_state.session_id,
                    "Created At Unix": msg['createdatunix'],
                    "Created At Datetime": msg['createdatdatetime']
                }
                df_temp = pd.DataFrame([new_row_messages])
                df_temp.to_csv('data/message_log.csv', mode='a', index=False, header=False)
                df_temp = pd.DataFrame(columns=df_temp.columns)
                df_messages = df_messages._append(new_row_messages, ignore_index=True)
                st.session_state.dataframe_messages = st.session_state.dataframe_messages._append(new_row_messages, ignore_index=True)
            st.dataframe(df_messages, use_container_width=True)
        with tab5:
            uploaded_file = st.file_uploader(
                label="Upload additional assistant file"
            )
            if uploaded_file:
                new_asst_file = client.files.create(
                    file=uploaded_file,
                    purpose="assistants"
                )
                new_asst_file_id = new_asst_file.id
                add_file_to_asst_response = client.beta.assistants.files.create(
                    file_id=new_asst_file_id,
                    assistant_id=st.session_state.assistant.id
                )
                check_id = add_file_to_asst_response.id
                if check_id:
                    st.success(body="File has been added!")
                else:
                    st.error(body="File was not uploaded. Please try again.")
