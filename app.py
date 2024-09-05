import os
import tempfile
import streamlit as st
from streamlit_chat import message
from rag import ChatPDF
import ollama
import json
from datetime import datetime

st.set_page_config(page_title="Dirty Rag")

def display_messages():
    st.subheader("Chat")
    chat_container = st.container()
    with chat_container:
        for i, (msg, is_user) in enumerate(st.session_state["messages"]):
            message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()


def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner("Thinking"):
            agent_text = st.session_state["assistant"].ask(user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))

        # Clear the input box
        st.session_state["user_input"] = ""


def read_and_save_file():
    st.session_state["user_input"] = ""

    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {file.name}"):
            st.session_state["assistant"].ingest(file_path)
        os.remove(file_path)

    st.success("Document(s) ingested successfully!")

def change_model():
    new_model = st.session_state["model_selector"]
    st.session_state["assistant"].set_model(new_model)
    st.success(f"Model changed to {new_model}")
    # Clear the conversation when changing models
    st.session_state["messages"] = []
    st.session_state["assistant"].clear()

def get_ollama_models():
    models = ollama.list()
    return [model['name'] for model in models['models']]

def clear_conversation():
    st.session_state["messages"] = []
    st.session_state["assistant"].clear()
    st.success("Conversation cleared!")

def save_conversation():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(st.session_state["messages"], f)
    st.success(f"Conversation saved as {filename}")

def load_conversation():
    uploaded_file = st.file_uploader("Choose a conversation file", type="json")
    if uploaded_file is not None:
        conversations = json.load(uploaded_file)
        st.session_state["messages"] = conversations
        st.success("Conversation loaded successfully!")

def page():
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["assistant"] = ChatPDF("mistral")

    st.header("Dirty Rag")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        available_models = get_ollama_models()
        st.selectbox("Select Model", available_models, key="model_selector", on_change=change_model)
    with col2:
        st.button("Clear Conversation", on_click=clear_conversation)
    with col3:
        st.button("Save Conversation", on_click=save_conversation)
    with col4:
        st.button("Load Conversation", on_click=load_conversation)

    st.subheader("Upload a document")
    st.file_uploader(
        "Upload document",
        type=["pdf"], #, "txt", "doc", "docx", "epub", "md", "py", "cpp", "cs", "html", "js"],
        key="file_uploader",
        on_change=read_and_save_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
    )

    st.session_state["ingestion_spinner"] = st.empty()

    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)


if __name__ == "__main__":
    page()