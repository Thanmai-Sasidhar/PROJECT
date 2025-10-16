import streamlit as st
from auth import add_user, init_db

def run_signup():
    st.title("🆕 Create an Account")
    init_db()

    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up", use_container_width=True):
        if not username or not password:
            st.warning("⚠️ Please fill all fields")
        elif password != confirm:
            st.warning("⚠️ Passwords do not match")
        else:
            if add_user(username, password):
                st.success("✅ Account created successfully! Please login.")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("🚫 Username already exists. Try another.")

    st.markdown("---")
    st.write("Already have an account?")
    if st.button("🔑 Go to Login", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()
