from fastmcp import FastMCP
from typing import Dict, Any
import os
from datetime import datetime

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

BASE_ALLOWED_FOLDER = os.path.abspath("../Documentos")

mcp = FastMCP("UEA-Regulations-PDF-MCP")

def _safe_path(path: str) -> str:
    if path.startswith("file://"):
        path = path[7:]
    if not os.path.isabs(path):
        path = os.path.join(BASE_ALLOWED_FOLDER, path)
    path = os.path.normpath(path)
    if not path.startswith(os.path.normpath(BASE_ALLOWED_FOLDER)):
        raise ValueError("Access denied: path outside allowed folder.")
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return path

def _read_pdf_text(path: str) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf não está instalado no servidor MCP.")
    path = _safe_path(path)
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(text)
    return "\n\n".join(pages).strip()

@mcp.tool
def list_pdfs(folder: str = "") -> Dict[str, Any]:
    base = BASE_ALLOWED_FOLDER
    candidate = os.path.join(BASE_ALLOWED_FOLDER, folder) if folder else base
    candidate = os.path.normpath(candidate)

    if not candidate.startswith(os.path.normpath(BASE_ALLOWED_FOLDER)):
        return {"ok": False, "error": "Access denied to folder."}

    pdfs = []
    for root, _, files in os.walk(candidate):
        for fn in files:
            if fn.lower().endswith(".pdf"):
                pdfs.append(os.path.join(root, fn))

    return {"ok": True, "files": pdfs}

@mcp.tool
def read_pdf(path: str) -> Dict[str, Any]:
    try:
        abs_path = _safe_path(path)
        text = _read_pdf_text(abs_path)
        meta = {
            "path": abs_path,
            "size_bytes": os.path.getsize(abs_path),
            "modified": datetime.fromtimestamp(os.path.getmtime(abs_path)).isoformat(),
        }
        return {"ok": True, "metadata": meta, "text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool
def extract_page(path: str, page_number: int) -> Dict[str, Any]:
    try:
        abs_path = _safe_path(path)
        if PdfReader is None:
            raise RuntimeError("pypdf não instalado.")
        reader = PdfReader(abs_path)
        total = len(reader.pages)

        if page_number < 1 or page_number > total:
            return {"ok": False, "error": f"Página fora do intervalo. Total: {total}"}

        page = reader.pages[page_number - 1]
        text = page.extract_text() or ""

        return {"ok": True, "page_number": page_number, "text": text, "total_pages": total}

    except Exception as e:
        return {"ok": False, "error": str(e)}

@mcp.tool
def find_section_by_heading(path: str, heading_keyword: str) -> Dict[str, Any]:
    try:
        abs_path = _safe_path(path)
        text = _read_pdf_text(abs_path)
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        for i, ln in enumerate(lines):
            if heading_keyword.lower() in ln.lower():
                start = max(0, i - 2)
                end = min(len(lines), i + 12)
                block = "\n".join(lines[start:end])
                return {"ok": True, "heading": lines[i], "block": block}

        return {"ok": False, "error": "Heading não encontrado."}

    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run()
