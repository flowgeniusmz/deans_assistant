# 0. Import Libraries
import streamlit as st
from config import pagesetup as ps
from app import display_title as disTitle, session_states as ss
from streamlit_extras.stylable_container import stylable_container

#with open( "config/style.css" ) as css:
    #st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)



# 1. Page Setup
## (Page Information)
app_name = "Dean's Assistant"
app_layout = "wide"
app_sidebar = "collapsed"
page_title = "Dean's Assistant"
page_subtitle = "Home" 
page_icon = st.secrets.paths.icon
page_description = "Allows school administration to quickly get information and insight."
overview_header = "Overview"
overview_text = f"**{page_title}** {page_description.lower()}"

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

# 2. Set Initial Session States
ss.get_initial_session_states()

# 3. Set Links
main_container = st.container(border=False)
with main_container:
    cc_links = st.columns(3)
    with cc_links[0]:
        link_container1 = st.container(border=True)
        with link_container1:
            link_chat = st.page_link(
                page="pages/1_Assistant_Chat.py", 
                label="Assistant Chat",
                icon = "💬"
            )
            exp_chat = st.expander(
                label="About",
                expanded=False
            )
            with exp_chat:
                st.markdown("Assistant Chat allows you to ask any question.")
    with cc_links[1]:
        link_container2 = st.container(border=True)
        with link_container2:
            link_admin = st.page_link(
                page="pages/2_Manage_Assistant.py",
                label="Manage Assistant",
                icon="🛠️"
            )
            exp_admin = st.expander(
                label="About",
                expanded=False
            )
            with exp_admin:
                st.markdown("Manage your assistant right from the app.")
    with cc_links[2]:
        link_container2 = st.container(border=True)
        with link_container2:
            link_history = st.page_link(
                page="pages/3_Chat_History.py",
                label="Chat History",
                icon="💬"
            )
            exp_history = st.expander(
                label="About",
                expanded=False
            )
            with exp_history:
                st.markdown("View your chat history.")
    
