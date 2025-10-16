import numpy as np
import cv2
from PIL import Image
import pytesseract
import streamlit as st

# -------------------- Session State Initialization --------------------
def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = {}
    if "chat_counter" not in st.session_state:
        st.session_state.chat_counter = 1
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None
    if "rename_chat" not in st.session_state:
        st.session_state.rename_chat = None
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a helpful assistant."
    if "model_choice" not in st.session_state:
        st.session_state.model_choice = "Gemini API"

    if not st.session_state.history:
        cid = f"chat_{st.session_state.chat_counter}"
        st.session_state.chat_counter += 1
        st.session_state.current_chat = cid
        st.session_state.history[cid] = {
            "name": "Default Chat",
            "messages": [{"role": "system", "content": st.session_state.system_prompt}]
        }
    elif st.session_state.current_chat is None:
        st.session_state.current_chat = list(st.session_state.history.keys())[0]

# -------------------- OCR Function --------------------
def extract_text_from_image(image: Image.Image) -> str:
    try:
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        text = pytesseract.image_to_string(gray)
        return text.strip()
    except Exception as e:
        return f"❌ OCR Error: {e}"
