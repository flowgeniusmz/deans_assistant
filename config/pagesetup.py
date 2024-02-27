import streamlit as st
import streamlit.components.v1 as c
from streamlit_elements import elements, mui, html
import hydralit_components as hc
import extra_streamlit_components as stx
from streamlit_extras.metric_cards import style_metric_cards

## 1. TITLE and SUBTITLE
def set_title(varTitle, varSubtitle):
        st.markdown(f"""<span style="font-weight: bold; font-size: 2em; color:#00b084;">{varTitle} </span> <span style="font-weight: bold; color:#0096D7; font-size:1.3em;">{varSubtitle}</span>""", unsafe_allow_html=True)
        st.divider()

def set_title_nodiv(varTitle, varSubtitle):
        st.markdown(f"""<span style="font-weight: bold; font-size: 2em; color:#00b084;">{varTitle} </span> <span style="font-weight: bold; color:#0096D7; font-size:1.3em;">{varSubtitle}</span>""", unsafe_allow_html=True)


### 2.  Wording
def set_blue_header(varSubtitle):
    st.markdown(f"""<span style="font-weight: bold; color:#0096D7; font-size:1.3em;">{varSubtitle}</span>""", unsafe_allow_html=True)
    

def set_green_header(varSubtitle):
    st.markdown(f"""<span style="font-weight: bold; color:#00b084; font-size:1.3em;">{varSubtitle}</span>""", unsafe_allow_html=True)

### PAGE LINKS ####

def get_pagelinks():

    container_pagelinks = st.container()
    with container_pagelinks:
        st.page_link("Home.py", label="Home", icon="🌐")
        st.page_link("pages/1_Page1.py", label="AI Assistant", icon="🌐")
        st.page_link("pages/2_Page2.py", label="Page 2", icon="🌐")

### 3. PAGE OVERVIEW
def set_page_overview(varHeader, varText):
        set_blue_header(varHeader)
        st.markdown(f"{varText}")
        st.divider()

### 3. PAGE SECTION
def set_page_section(varHeader, varText):
        set_blue_header(varHeader)
        st.markdown(f"{varText}")
        section_placeholder = st.empty()
        st.divider()
        return section_placeholder

### 4. HYDRALIT NAVBAR

def set_nav_bar():
        navbar_menu_items = [
                {'icon': "far fa-chart-bar", 'label':"Item1", 'ttip': "tooltip"},
                {'icon': "fas fa-tachometer-alt", 'label':"Item2",'ttip':"tooltip"},
                {'icon': "far fa-copy", 'label':"Item3", 'ttip': "Tooltip", 'submenu': [{'icon': "fa fa-paperclip", 'label': "Subitem1"}, {'icon': "fa fa-database", 'label': "subitem2"}, {'icon': "far fa-copy", 'label': "Subitem3"}]}
        ]
        over_theme = {'txc_inactive': '#FFFFFF'}
        menu_id = hc.nav_bar(
                menu_definition = navbar_menu_items, 
                override_theme = over_theme,
                home_name = "Home",
                login_name = "Logout",
                hide_streamlit_markers=False,
                sticky_nav = True,
                sticky_mode = "pinned"
        )

### 5. TITLE + PAGE OVERVIEW
def set_title_pageoverview(varTitle, varSubtitle, varHeader, varSubheader):
    container0 = st.container()
    with container0:
        set_title(varTitle, varSubtitle)
    
    container1=st.container()
    with container1:
        set_page_overview(varHeader, varSubheader)
        


# 1. KPI METRIC STYLING - Create container with # of columns = to # of metrics in a metrics dictionary
def get_metric_container(varMetrics):
    metrics = varMetrics      #array of metrics dictionary {"lablel": "", "id": "", "value": #, "delta": #}
    lenMetrics = len(metrics)
    cols = st.columns(lenMetrics)

    for idx, metric in enumerate(metrics):
        cols[idx].metric(label=metric["label"], value=metric["value"], delta=metric["delta"])
    style_metric_cards(
         border_left_color="#0096D7",
         border_color="#0096D7",
         box_shadow=True
    )

  #"""
 #   Applies a custom style to st.metrics in the page

  #  Args:
 #       background_color (str, optional): Background color. Defaults to "#FFF".
  #      border_size_px (int, optional): Border size in pixels. Defaults to 1.
  #      border_color (str, optional): Border color. Defaults to "#CCC".
  #      border_radius_px (int, optional): Border radius in pixels. Defaults to 5.
  #      border_left_color (str, optional): Borfer left color. Defaults to "#9AD8E1".
  #      box_shadow (bool, optional): Whether a box shadow is applied. Defaults to True.
  #  """

  #https://arnaudmiribel.github.io/streamlit-extras/extras/metric_cards/     
