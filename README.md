![Dirty RAG](https://github.com/user-attachments/assets/1b6a1c49-2b96-4ae4-8f6b-048c9e287eeb)
# Dirty Rag

This is a Retrieval-Augmented Generation (RAG) chat application built with Streamlit and LangChain. It allows users to upload documents, chat with an AI assistant, and receive responses based on the content of the uploaded documents.

## Features
- Support for regular chat and RAG document retrieval
- Modern web ui interface with ai assistant
- Support for pdf, txt, doc/docx, csv, and py files
- Saving and Loading of conversations
- Dropdown to choose model (Any model available to Ollama is available)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/wiseyoungfool/dirty-rag.git
   cd dirty-rag
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have Ollama installed and running on your system. Visit [Ollama's website](https://ollama.ai/) for installation instructions. You will need at least one model to use with the application.

## Usage

1. Start the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to the URL displayed in the terminal (usually `http://localhost:8501`).

3. Use the interface to:
   - Select an AI model
   - Upload documents
   - Chat with the AI assistant
   - Manage conversations

## File Structure

- `app.py`: Main Streamlit application and UI
- `rag.py`: RAG implementation using LangChain
- `requirements.txt`: List of Python dependencies

## License

This project is licensed under the MIT License.
