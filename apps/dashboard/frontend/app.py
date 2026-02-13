"""
ToneSoul 5.2 Frontend
人性化前端入口

運行方式：
    streamlit run frontend/app.py
"""

import streamlit as st
from pages import history, memory, skills, terrain, workspace
from utils.theme import apply_theme

st.set_page_config(
    page_title="語魂工作區",
    page_icon="語魂",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

st.sidebar.title("語魂")

page = st.sidebar.radio(
    "導航",
    ["技能區", "工作區", "我的記憶", "語義地圖", "回顧"],
    format_func=lambda x: x,
)

if page == "技能區":
    skills.render()
elif page == "工作區":
    workspace.render()
elif page == "我的記憶":
    memory.render()
elif page == "語義地圖":
    terrain.render()
elif page == "回顧":
    history.render()
