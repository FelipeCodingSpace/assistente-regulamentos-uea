from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.retrieval_qa.base import RetrievalQA

DB_PATH = "vector_db"
PROJECT_ID = "gen-lang-client-0516972642" # ID do projeto
LOCATION = "us-central1" # Região
MODEL_NAME = "projects/561885827365/locations/us-central1/endpoints/4371120570851393536"
EMBEDDING_MODEL_NAME = "models/embedding-001" 

def get_rag_chain():
    llm = ChatVertexAI(
            model_name=MODEL_NAME,
            temperature=0.1,
            project=PROJECT_ID,
            location=LOCATION
        )
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={'k': 5})

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