import streamlit as st
from auth import validate_user, init_db

def run_login():
    st.title("🔐 Login to Continue")
    init_db()  # Ensure DB exists

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if validate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "chat"
            st.success("✅ Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.markdown("---")
    st.write("Don't have an account?")
    if st.button("📝 Go to Signup", use_container_width=True):
        st.session_state.page = "signup"
        st.rerun()
