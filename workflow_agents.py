import os
from langchain_google_vertexai import ChatVertexAI
from rag_pipeline import get_rag_chain
from mcp_tools.client_tools import mcp_list_pdfs, mcp_get_table_of_contents

PROJECT_ID = "gen-lang-client-0516972642" # ID do projeto
LOCATION = "us-central1" # Região

class AgenteBase:
    """
    Agente base que implementa a função de pensar que é utilizada por todos os agentes.
    """
    def __init__(self, nome: str, temperatura: float = 0.1):
        self.nome = nome
        self.model = "projects/561885827365/locations/us-central1/endpoints/4371120570851393536"
        self.temperatura = temperatura
        self.llm = ChatVertexAI(
            model_name=self.model,
            temperature=self.temperatura,
            project=PROJECT_ID,
            location=LOCATION,
            convert_system_message_to_human=False 
        )

    def pensar(self, instrucoes: str, entrada: str) -> str:
        return self.llm.invoke(f"{instrucoes}\n\nEntrada:\n{entrada}").content.strip()

class AnalyzerAgent(AgenteBase):
    """
    Este agente recebe o tipo de rota e adapta sua análise.
    Sua saída inclui uma instrução para o próximo agente.
    """
    def executar(self, texto_bruto: str, rota: str, pergunta_original: str) -> str:
        if rota == "RAG":
            # Lógica para analisar o contexto de uma pergunta
            instrucoes = f"""
Você é um agente analisador especialista em regulamentos acadêmicos.
Sua tarefa é analisar o TEXTO DE CONTEXTO abaixo e extrair os pontos essenciais para responder à PERGUNTA DO USUÁRIO.
A sua saída DEVE ser uma análise clara e objetiva. No final, adicione a seguinte instrução para o próximo agente:
[TAREFA_FINAL: Use esta análise para responder diretamente à pergunta do usuário sobre '{pergunta_original}'.]

---
PERGUNTA DO USUÁRIO:
{pergunta_original}

---
TEXTO DE CONTEXTO:
"""
            return self.pensar(instrucoes, texto_bruto)
        
        elif rota == "MCP":
            # Lógica para analisar e formatar um sumário
            instrucoes = """
Você é um agente formatador de documentos.
Sua tarefa é analisar o SUMÁRIO abaixo e prepará-lo para exibição.
A sua saída DEVE ser apenas o sumário formatado de forma limpa. No final, adicione a seguinte instrução para o próximo agente:
[TAREFA_FINAL: Apresente este sumário formatado para o usuário, usando uma lista de bullet points.]

---
SUMÁRIO:
"""
            return self.pensar(instrucoes, texto_bruto)
        
        else:
            return "Rota desconhecida. Não é possível analisar."

class AnswerAgent(AgenteBase):
    """
    Este agente  recebe uma análise que contém uma instrução sobre o que fazer.
    """
    def executar(self, analise_com_instrucao: str) -> str:
        # O prompt é mais geral, pois a instrução específica virá da entrada
        instrucoes = """
Você é o assistente virtual da UEA, amigável e prestativo.
Sua tarefa é seguir a instrução contida na ANÁLISE para gerar a resposta final para o estudante.
Use formatação Markdown (negrito, listas) para tornar a resposta clara e legível.
Se a instrução for para responder a uma pergunta, termine com um lembrete para consultar a secretaria para informações oficiais.
Se a instrução for para apresentar um sumário, adicione uma frase de introdução e conclusão amigáveis.

---
ANÁLISE E INSTRUÇÃO:
"""
        return self.pensar(instrucoes, analise_com_instrucao)
    
class DocumentSelectorAgent(AgenteBase):
    """
    Este agente é um especialista em escolher o arquivo PDF mais relevante
    de uma lista, com base na pergunta do usuário.
    """
    def executar(self, pergunta: str, documentos: list[str]) -> str:
        # Formata a lista de documentos para o LLM entender
        doc_list_str = "\n".join([f"- {os.path.basename(doc)}" for doc in documentos])

        instrucoes = f"""
Você é um bibliotecário especialista. Sua tarefa é selecionar o documento MAIS RELEVANTE de uma lista para responder à pergunta do usuário.
Os nomes dos arquivos são descritivos. Analise a pergunta e os nomes dos arquivos.
Pergunta do usuário:
"{pergunta}"
Lista de documentos disponíveis:
{doc_list_str}
Responda APENAS com o nome do arquivo escolhido. Não adicione nenhuma outra palavra.
"""
        
        # A entrada é vazia, pois as instruções já contêm tudo
        nome_arquivo_escolhido = self.pensar(instrucoes, "")

        # Validação: Procura o nome do arquivo retornado pelo LLM na lista original
        for doc_path in documentos:
            if nome_arquivo_escolhido in doc_path:
                return doc_path # Retorna o caminho completo

        # Fallback de segurança: se a validação falhar, retorna o primeiro da lista
        print("[SELECTOR-WARN] A escolha do LLM não foi validada. Usando o primeiro PDF como fallback.")
        return documentos[0]

class RouterAgent(AgenteBase):
    def executar(self, pergunta: str) -> str:
        instrucoes = """Você é um roteador. 
        Use 'MCP' se a pergunta mencionar: sumário, índice, estrutura, seções, capítulos. 
        Caso contrário, use 'RAG'. Responda apenas com MCP ou RAG."""
        return self.pensar(instrucoes, pergunta).upper().strip()

def executar_rag(pergunta: str) -> str:
    from rag_pipeline import get_rag_chain
    chain = get_rag_chain()
    try: return chain.invoke(pergunta).get("result", "Não foi possível encontrar informações.")
    except Exception as e: print(f"[WORKFLOW-ERROR] Erro no RAG: {e}"); return "Erro ao buscar informações."

def executar_mcp(pergunta: str, seletor: DocumentSelectorAgent) -> str:
    """Usa as ferramentas do MCP. Agora focado em buscar o sumário."""
    pdfs_response = mcp_list_pdfs()
    print(f"[MCP-DEBUG] Resposta de mcp_list_pdfs(): {pdfs_response}")

    if not pdfs_response.get("ok") or not pdfs_response.get("files"):
        return "Nenhum documento PDF foi encontrado na base de conhecimento."
    
    lista_de_pdfs = pdfs_response["files"]
    pdf_selecionado = ""

    if len(lista_de_pdfs) == 1:
        # Se só há um PDF, não há o que escolher.
        pdf_selecionado = lista_de_pdfs[0]
        print(f"[MCP-INFO] Apenas um PDF encontrado. Selecionando: {os.path.basename(pdf_selecionado)}")
    else:
        # Se há múltiplos PDFs, aciona o agente seletor.
        print(f"[MCP-INFO] Múltiplos PDFs encontrados. Acionando DocumentSelectorAgent...")
        pdf_selecionado = seletor.executar(pergunta, lista_de_pdfs)
        print(f"[MCP-INFO] Agente selecionou o documento: {os.path.basename(pdf_selecionado)}")

    result = mcp_get_table_of_contents(pdf_selecionado)
    if result.get("ok"):
        return result.get("table_of_contents", "Sumário vazio.")
    else:
        return result.get("error", "Ocorreu um erro ao extrair o sumário.")

def executar_workflow(pergunta: str) -> str:
    router = RouterAgent("Router")
    analisador = AnalyzerAgent("Analyzer")
    gerador = AnswerAgent("Answer")
    seletor = DocumentSelectorAgent("Selector")

    rota = router.executar(pergunta)
    print(f"[WORKFLOW-INFO] Rota escolhida: {rota}")
    texto_bruto = executar_mcp(pergunta, seletor) if rota == "MCP" else executar_rag(pergunta)
    if "não encontrei" in texto_bruto.lower() or "nenhum pdf" in texto_bruto.lower():
        return texto_bruto
    analise = analisador.executar(texto_bruto, rota, pergunta)
    resposta_final = gerador.executar(analise)
    return resposta_final