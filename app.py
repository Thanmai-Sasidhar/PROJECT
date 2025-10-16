import os
import io
import streamlit as st
import google.generativeai as genai
import ollama
from PIL import Image
from utils import extract_text_from_image, init_session_state

# -------------------- Constants --------------------
GEMINI_MODEL = "gemini-2.5-flash"
OLLAMA_MODEL = "llama3.1:8b"

# -------------------- Functions --------------------
def configure_api():
    """Configure Gemini API if key exists."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.warning("❌ GEMINI_API_KEY not found in environment variables.")
        return None
    genai.configure(api_key=api_key)
    return api_key


def safe_login_redirect():
    """Redirect user to login if not logged in."""
    if not st.session_state.get("logged_in", False):
        st.warning("⚠️ Please login first.")
        st.session_state.page = "login"
        st.stop()


def logout_button():
    """Add logout button to sidebar."""
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.experimental_rerun()


def choose_model():
    """Sidebar radio to select model."""
    st.sidebar.markdown("## 🤖 Choose Model")
    st.session_state.model_choice = st.sidebar.radio(
        "Select Model:", ["Gemini API", "Ollama Local"]
    )


def new_chat_button():
    """Sidebar button to create a new chat."""
    if st.sidebar.button("➕ New Chat", use_container_width=True):
        cid = f"chat_{st.session_state.chat_counter}"
        st.session_state.chat_counter += 1
        st.session_state.current_chat = cid
        st.session_state.history[cid] = {
            "name": "New Chat",
            "messages": [{"role": "system", "content": st.session_state.system_prompt}]
        }


def ocr_tool():
    """Handle OCR image upload and send text to chat."""
    st.sidebar.markdown("## 📷 OCR Tool")
    uploaded_file = st.sidebar.file_uploader("Upload image for OCR", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=200)

        ocr_text = extract_text_from_image(image)
        if ocr_text:
            st.success("✅ Text extracted from image")
            chat = st.session_state.history[st.session_state.current_chat]
            chat["messages"].append({"role": "user", "content": f"OCR Extracted Text:\n{ocr_text}"})
            generate_assistant_reply(chat)


def chat_history_sidebar():
    """Show chat history in sidebar with rename/delete options."""
    st.sidebar.markdown("## 💾 Chat History")
    for cid, chat in st.session_state.history.items():
        cols = st.sidebar.columns([0.8, 0.2])
        if cols[0].button(chat["name"], key=f"chat_{cid}", use_container_width=True):
            st.session_state.current_chat = cid
        if cols[1].button("⋮", key=f"menu_{cid}"):
            st.session_state.rename_chat = cid
        if st.session_state.get("rename_chat") == cid:
            new_name = st.text_input("Rename", chat["name"], key=f"rename_input_{cid}")
            if st.button("✅ Save", key=f"save_{cid}"):
                st.session_state.history[cid]["name"] = new_name or chat["name"]
                st.session_state.rename_chat = None
            if st.button("🗑 Delete", key=f"delete_{cid}"):
                del st.session_state.history[cid]
                st.session_state.rename_chat = None
                st.session_state.current_chat = (
                    list(st.session_state.history.keys())[0]
                    if st.session_state.history else None
                )
                st.experimental_rerun()


def generate_assistant_reply(chat):
    """Generate assistant response using chosen model."""
    placeholder, full_text = st.empty(), ""
    try:
        if st.session_state.model_choice == "Gemini API" and st.session_state.api_key:
            model = genai.GenerativeModel(GEMINI_MODEL)
            stream = model.generate_content(
                [m["content"] for m in chat["messages"] if m["role"] in ("system", "user")],
                stream=True
            )
            for chunk in stream:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text)
        else:
            stream = ollama.chat(model=OLLAMA_MODEL, messages=chat["messages"], stream=True)
            for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    c = chunk["message"]["content"]
                    full_text += c
                    placeholder.markdown(full_text)
    except Exception as e:
        placeholder.error(f"❌ Error: {e}")
    chat["messages"].append({"role": "assistant", "content": full_text})


def chat_ui():
    """Main chat interface."""
    st.title("💬 Chat with Gemini or Ollama")
    if not st.session_state.current_chat:
        st.info("Start a new chat from the sidebar ➕")
        return

    chat = st.session_state.history[st.session_state.current_chat]
    for msg in chat["messages"]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    prompt = st.chat_input("Ask something...")
    if prompt:
        if chat["name"] in ["New Chat", "Default Chat"]:
            chat["name"] = prompt[:40] + ("..." if len(prompt) > 40 else "")
        chat["messages"].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            generate_assistant_reply(chat)

        # Download chat
        if len(chat["messages"]) > 1:
            txt = "".join([f"{m['role'].upper()}: {m['content']}\n\n"
                           for m in chat["messages"] if m["role"] != "system"])
            st.download_button(
                "📤 Share Current Chat",
                data=io.BytesIO(txt.encode()),
                file_name=f"{chat['name'].replace(' ', '_')}.txt",
                mime="text/plain"
            )


# -------------------- Main Chat Runner --------------------
def run_chat():
    st.set_page_config(page_title="Gemini + Ollama Chat", page_icon="🤖", layout="centered")
    init_session_state()

    safe_login_redirect()
    st.session_state.api_key = configure_api()
    logout_button()
    choose_model()
    new_chat_button()
    ocr_tool()
    chat_history_sidebar()
    chat_ui()
