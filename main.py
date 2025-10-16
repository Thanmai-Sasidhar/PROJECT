import streamlit as st
from login import run_login
from signup import run_signup
from app import run_chat

st.set_page_config(page_title="Chatbot App", page_icon="🤖", layout="centered")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Page router
if st.session_state.page == "login":
    run_login()
elif st.session_state.page == "signup":
    run_signup()
elif st.session_state.page == "chat":
    run_chat()
