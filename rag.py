from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.prompts import PromptTemplate
from langchain.vectorstores.utils import filter_complex_metadata
from langchain.memory import ConversationBufferMemory


class ChatPDF:
    def __init__(self, model):
        self.model = ChatOllama(model=model)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.memory = ConversationBufferMemory(k=10, return_messages=True)
        self.prompt = PromptTemplate.from_template(
            """
            <s> [INST] You are an AI assistant. Use the following pieces of retrieved context if it is available to answer the question.
            If there is no context, answer to the best of your ability. If you don't know the answer, just say that you don't know.
            Keep the answer as concise as you can. [/INST] </s>
            [INST]
            History: {history}
            Question: {question}
            Context: {context}
            Answer: [/INST]
            """
        )
        self.retriever = None
        self.chain = None
        self.setup_chain()

    def setup_chain(self):
        def get_context(input_dict):
            if self.retriever:
                return self.retriever.get_relevant_documents(input_dict["question"])
            return []

        self.chain = (
            {
                "context": RunnableLambda(get_context),
                "question": RunnablePassthrough(),
                "history": lambda x: self.memory.load_memory_variables({})["history"]
            }
            | self.prompt
            | self.model
            | StrOutputParser()
        )

    def ingest(self, file_path: str):
        loader = PyPDFLoader(file_path=file_path)
        
        docs = loader.load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        vector_store = Chroma.from_documents(documents=chunks, embedding=FastEmbedEmbeddings())
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.5,
            },
        )

    def ask(self, query: str):
        if self.chain is None:
            self.setup_chain()
        response = self.chain.invoke({"question": query})
        self.memory.save_context({"input": query}, {"output": response})
        return response

    def clear(self):
        self.vector_store = None
        self.retriever = None

    def set_model(self, model: str):
        self.model = ChatOllama(model=model)
        self.setup_chain()