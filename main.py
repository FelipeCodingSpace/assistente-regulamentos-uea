import streamlit as st
from dotenv import load_dotenv
import traceback
from workflow_agents import executar_workflow

if "env" not in st.session_state:
    load_dotenv()
    st.session_state.env = True

st.set_page_config(page_title="Assistente de Regulamentos UEA", layout="wide")

st.title("💬 Assistente Virtual de Regulamentos Acadêmicos da UEA")
st.caption("Faça perguntas gerais ou específicas (ex: 'o que diz o artigo 10?') sobre os regulamentos.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso ajudar com os regulamentos hoje?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Quais são os critérios para trancamento de matrícula?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando os documentos e preparando sua resposta..."):
            try:
                response = executar_workflow(prompt)
                st.markdown(response)
            except Exception as e:
                st.error("Ocorreu um erro ao processar sua solicitação.")
                traceback.print_exc()
                response = "Desculpe, não consegui processar sua pergunta."

    st.session_state.messages.append({"role": "assistant", "content": response})