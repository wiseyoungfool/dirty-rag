import os
import tempfile
import streamlit as st
from streamlit_chat import message
from rag import ChatPDF
import ollama

st.set_page_config(page_title="Dirty Rag")


def display_messages():
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()


def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            agent_text = st.session_state["assistant"].ask(user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))


def read_and_save_file():
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {file.name}"):
            st.session_state["assistant"].ingest(file_path)
        os.remove(file_path)

def change_model():
    st.session_state["assistant"].set_model(st.session_state["model_selector"])

def get_ollama_models():
    models = ollama.list()
    return [model['name'] for model in models['models']]

def page():
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["assistant"] = ChatPDF("mistral")

    st.header("Dirty Rag")

    available_models = get_ollama_models()
    selected_model = st.selectbox("Select Model", available_models, key="model_selector", on_change=change_model)

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