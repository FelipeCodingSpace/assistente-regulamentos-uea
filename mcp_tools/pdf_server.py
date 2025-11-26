import os
import sys
from datetime import datetime
from typing import Dict, Any, List
from fastmcp import FastMCP

try:
    from pypdf import PdfReader
    from pypdf.generic import Destination
except ImportError:
    PdfReader = None
    Destination = None

def main():
        
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    BASE_ALLOWED_FOLDER = os.path.join(PROJECT_ROOT, 'Documentos')
    mcp = FastMCP("UEA-Regulations-PDF-MCP")

    def _safe_path(path: str) -> str:
        if path.startswith("file://"): path = path[7:]
        if not os.path.isabs(path): path = os.path.join(BASE_ALLOWED_FOLDER, path)
        path = os.path.normpath(path)
        if not path.startswith(os.path.normpath(BASE_ALLOWED_FOLDER)): raise ValueError("Acesso negado.")
        if not os.path.exists(path): raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        return path

    def _read_pdf_text(path: str) -> str:
        if PdfReader is None: raise RuntimeError("'pypdf' não está instalado.")
        reader = PdfReader(_safe_path(path))
        return "\n\n".join([(p.extract_text() or "") for p in reader.pages]).strip()

    @mcp.tool
    def list_pdfs(folder: str = "") -> Dict[str, Any]:
        candidate = os.path.join(BASE_ALLOWED_FOLDER, folder) if folder else BASE_ALLOWED_FOLDER
        candidate = os.path.normpath(candidate)
        if not candidate.startswith(os.path.normpath(BASE_ALLOWED_FOLDER)): return {"ok": False, "error": "Acesso negado."}
        pdfs = [os.path.join(root, fn) for root, _, files in os.walk(candidate) for fn in files if fn.lower().endswith(".pdf")]
        return {"ok": True, "files": pdfs}
    
    @mcp.tool
    def get_table_of_contents(path: str) -> Dict[str, Any]:
        """Extrai o sumário (bookmarks/outline) de um arquivo PDF."""
        try:
            if PdfReader is None: raise RuntimeError("'pypdf' não está instalado.")
            
            abs_path = _safe_path(path)
            reader = PdfReader(abs_path)
            
            if not reader.outline:
                return {"ok": False, "error": "Este documento PDF não contém um sumário (bookmarks)."}

            # Função recursiva para formatar o sumário aninhado
            def format_outline(outline: List[Destination], indent: int = 0) -> str:
                result = []
                for item in outline:
                    if isinstance(item, list):
                        result.append(format_outline(item, indent + 2))
                    else:
                        # O título do marcador está no atributo .title
                        title = item.title
                        # Adiciona indentação para mostrar a hierarquia
                        result.append(f"{' ' * indent}- {title}")
                return "\n".join(result)

            formatted_toc = format_outline(reader.outline)
            
            return {"ok": True, "table_of_contents": formatted_toc}
            
        except Exception as e:
            return {"ok": False, "error": str(e)}


    mcp.run()

if __name__ == "__main__":
    main()