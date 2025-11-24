import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

if os.getenv("GOOGLE_API_KEY") is None:
    print("ERRO: A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
    exit()

DATA_PATH = "Documentos/"
DB_PATH = "vector_db"

def main():
    print("Iniciando ingestão com embeddings do Google...")
    documents = [doc for f in os.listdir(DATA_PATH) if f.endswith('.pdf') for doc in PyPDFLoader(os.path.join(DATA_PATH, f)).load()]
    if not documents:
        print("Nenhum documento PDF carregado.")
        return
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Total de {len(chunks)} chunks de texto criados.")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_db = Chroma.from_documents(chunks, embeddings, persist_directory=DB_PATH)
    
    print("-" * 50)
    print("✅ Processo de ingestão concluído com sucesso!")
    print(f"O banco de dados vetorial foi salvo em: '{DB_PATH}'")
    print("-" * 50)

if __name__ == "__main__":
    main()