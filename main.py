# Arquivo: main.py

import streamlit as st
import traceback
from rag_pipeline import get_rag_chain

st.set_page_config(page_title="Assistente de Regulamentos UEA", layout="wide")
st.title("💬 Assistente Virtual de Regulamentos Acadêmicos da UEA")
st.caption("Faça perguntas sobre os regulamentos da universidade e receba respostas baseadas nos documentos oficiais (usando a API do Google Gemini).")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Quais são os critérios para trancamento de matrícula?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando os documentos e gerando a resposta..."):
            try:
                rag_chain = get_rag_chain()
                result_dict = rag_chain.invoke(prompt)
                response = result_dict["result"]
                st.markdown(response)
            except Exception as e:
                st.error("Ocorreu um erro ao processar sua solicitação.")
                print("="*50)
                print("ERRO DETALHADO NO STREAMLIT:")
                traceback.print_exc()
                print("="*50)
                response = "Desculpe, não consegui processar sua pergunta. Verifique o console para mais detalhes."

    st.session_state.messages.append({"role": "assistant", "content": response})