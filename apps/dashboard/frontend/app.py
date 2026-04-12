"""
ToneSoul 5.2 Frontend
人性化前端入口

運行方式：
    streamlit run frontend/app.py
"""

import streamlit as st
from pages import history, memory, overview, skills, terrain, workspace
from utils.theme import apply_theme

st.set_page_config(
    page_title="ToneSoul / 語魂",
    page_icon="語魂",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

st.sidebar.title("語魂")

_PAGES = [
    "首頁",
    "對話工作區",
    "技能控制台",
    "AI 記憶",
    "語義地圖",
    "決策回顧",
]

page = st.sidebar.radio("導航", _PAGES, format_func=lambda x: x)

if page == "首頁":
    overview.render()
elif page == "對話工作區":
    workspace.render()
elif page == "技能控制台":
    skills.render()
elif page == "AI 記憶":
    memory.render()
elif page == "語義地圖":
    terrain.render()
elif page == "決策回顧":
    history.render()
