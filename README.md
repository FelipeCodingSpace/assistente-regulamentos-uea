# Assistente Híbrido com Agentes Inteligentes (RAG + Ferramentas MCP)

Este projeto implementa um assistente de chat avançado que utiliza um sistema de múltiplos agentes de IA para responder perguntas sobre os regulamentos acadêmicos da Universidade do Estado do Amazonas (UEA).

O sistema combina duas abordagens de IA Generativa:
1.  **RAG (Retrieval-Augmented Generation):** Para responder a perguntas abertas e gerais, buscando informações em uma base de conhecimento vetorial.
2.  **Ferramentas Especializadas (MCP):** Para executar tarefas específicas e precisas, como extrair a estrutura (sumário) de um documento.

Um agente roteador inteligente analisa a pergunta do usuário e decide qual a melhor abordagem a ser utilizada, orquestrando um workflow de agentes especializados para construir a melhor resposta possível.

## Funcionalidades Principais

-   **Roteamento Inteligente:** Um `RouterAgent` decide automaticamente se a pergunta deve ser respondida com busca semântica (RAG) ou com uma ferramenta específica (MCP).
-   **Busca Semântica (RAG):** Responde a perguntas gerais (ex: `"Quais os critérios para trancamento?"`) com base no conteúdo dos PDFs.
-   **Ferramentas Especializadas (MCP):** Executa tarefas diretas, como a extração do sumário de um documento para entender sua estrutura.
-   **Seleção Inteligente de Documentos:** Um `DocumentSelectorAgent` escolhe o PDF mais relevante para a pergunta quando a rota MCP é acionada, caso existam múltiplos documentos.
-   **Workflow de Múltiplos Agentes:** As respostas são processadas em etapas por agentes especializados em análise e geração de texto, garantindo respostas mais coerentes e bem formatadas.
-   **Interface Web Simples:** Uma interface de chat amigável construída com Streamlit.

## Estrutura do Projeto

```
/assistente-regulamentos-uea/
|
|-- /Documentos/         # Coloque os PDFs dos regulamentos aqui
|-- /mcp_tools/          # Ferramentas do Multi-Tool Cooperative Protocol (MCP)
|   |-- client_tools.py  # Cliente para chamar as ferramentas do MCP
|   |-- pdf_server.py    # Servidor que define as ferramentas (ex: extrair sumário)
|
|-- /vector_db/          # Base de dados vetorial (criada automaticamente ao executar ingest.py)
|-- .env                 # Arquivo com chave de api do google para acessar o gemini
|-- ingest.py            # Script para processar e indexar os PDFs para o RAG
|-- main.py              # Interface web com Streamlit
|-- rag_pipeline.py      # Lógica da cadeia RAG com a API do Google
|-- workflow_agents.py   # O coração do projeto, onde todos os agentes são definidos
|-- requirements.txt     # Dependências do projeto
|-- README.md            # Este arquivo
```

## Pré-requisitos

1.  **Python 3.8 ou superior.**
2.  **Conta Google e Chave de API do Google AI Studio.**

## Guia de Instalação e Execução

### 1. Clone o Repositório

```bash
git clone https://github.com/FelipeCodingSpace/assistente-regulamentos-uea.git
cd assistente-regulamentos-uea
```

### 2. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 3. Configure sua Chave de API do Hugging Face

1.  Vá para [Google AI Studio](https://aistudio.google.com/app/api-keys) e gere uma nova chave de API.
2.  É necessário antes ativar a opção de faturamento do projeto relacionado a sua chave de API.
3.  Na pasta raiz do projeto, crie um arquivo chamado .env
4.  Dentro do arquivo .env, adicione a seguinte linha, substituindo SUA_CHAVE_AQUI pela chave que você copiou:

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
