import streamlit as st
from config import pagesetup as ps


def display_title_section(varTitle: str, varSubtitle: str):
    title_container = st.container()
    with title_container:
        title_columns = st.columns(2)
        with title_columns[0]:
            ps.set_title_nodiv(
                varTitle=varTitle,
                varSubtitle=varSubtitle
            )
        with title_columns[1]:
            st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQroYsyWjvZmkyguxf2_XUKqcWTNLkZrRbPzPL8MU5I&s', caption='Plainfield School District 202') #Streamlit image for branding
        st.divider()
        