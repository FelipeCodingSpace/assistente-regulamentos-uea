# Arquivo: rag_pipeline.py (VERSÃO FINAL E CORRIGIDA)

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

load_dotenv()

DB_PATH = "vector_db"
# MUDANÇA: Usando o modelo 'gemini-pro' para máxima estabilidade e compatibilidade.
MODEL_NAME = "models/gemini-2.5-flash-lite" 
EMBEDDING_MODEL_NAME = "models/embedding-001"

def get_rag_chain():
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.1, convert_system_message_to_human=True)
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={'k': 3})

    template = """
    Você é um assistente especializado nos regulamentos da Universidade do Estado do Amazonas (UEA).
    Use APENAS o contexto fornecido abaixo para responder à pergunta do usuário.
    Se a informação não estiver no contexto, diga "Não encontrei informações sobre isso nos documentos."
    Seja claro, conciso e responda em português.

    Contexto:
    {context}

    Pergunta:
    {question}

    Resposta:
    """
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )
    
    return rag_chain