# Assistente de Regulamentos Acadêmicos da UEA com IA Generativa (RAG)

Este projeto implementa um assistente de chat que utiliza IA Generativa e a técnica de RAG (Retrieval-Augmented Generation) para responder perguntas sobre os regulamentos acadêmicos da Universidade do Estado do Amazonas (UEA), baseando-se em documentos oficiais em formato PDF.

## Funcionalidades

-   **Consulta em Linguagem Natural:** Faça perguntas como se estivesse conversando com uma pessoa.
-   **Respostas Baseadas em Fontes:** As respostas são geradas com base no conteúdo dos documentos fornecidos.
-   **Interface Web Simples:** Interface amigável criada com Streamlit.

## Estrutura do Projeto

```
/assistente-regulamentos-uea/
|
|-- /Dataset/            # Dataset com PDFs dos regulamentos aqui
|-- /vector_db/          # Base de dados vetorial (criada automaticamente)
|-- .env                 # Arquivo para a chave de API (NÃO ENVIE PARA O GIT)
|-- ingest.py            # Script para processar e indexar os PDFs
|-- rag_pipeline.py      # Lógica principal do RAG com a API do Google
|-- main.py              # Interface web com Streamlit (ou main.py)
|-- requirements.txt     # Dependências do projeto
|-- README.md            # Este arquivo
```

## Pré-requisitos

1.  **Python 3.8 ou superior.**
2.  **Conta Google e Chave de API do Google AI Studio.**

## Guia de Instalação e Execução

### 1. Clone o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd assistente-regulamentos-uea
```

### 2. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 3. Configure sua Chave de API do Hugging Face

1.  Vá para [Google AI Studio](https://aistudio.google.com/app/api-keys) e gere uma nova chave de API.
2.  Na pasta raiz do projeto, crie um arquivo chamado .env
3.  Dentro do arquivo .env, adicione a seguinte linha, substituindo SUA_CHAVE_AQUI pela chave que você copiou:

```.env
GOOGLE_API_KEY="SUA_CHAVE_AQUI"
```

### 4. Processe e Indexe os Documentos

Este passo só precisa ser executado uma vez (ou sempre que você adicionar/atualizar os PDFs). Ele irá ler os documentos e criar a base de conhecimento.

```bash
python ingest.py
```

### 5. Inicie a Aplicação Web

Agora, inicie a interface do assistente.

```bash
streamlit run main.py
```