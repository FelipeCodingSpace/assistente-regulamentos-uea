import asyncio
from fastmcp import Client
from typing import Any, Dict, Optional
import json

MCP_SERVER_ENTRYPOINT = "mcp_tools/pdf_server.py"

async def _call_tool_async(tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        async with Client(MCP_SERVER_ENTRYPOINT) as client:
            res = await client.call_tool(tool, args)
            content_obj = res.content[0]
            if hasattr(content_obj, "text"): return json.loads(content_obj.text)
            else: return {"ok": False, "error": "Resposta inesperada do servidor MCP."}
    except Exception as e: return {"ok": False, "error": str(e)}

def call_tool_sync(tool: str, args: Dict[str, Any], timeout: Optional[float] = 30.0) -> Dict[str, Any]:
    try:
        return asyncio.run(asyncio.wait_for(_call_tool_async(tool, args), timeout))
    except Exception as e: return {"ok": False, "error": str(e)}


def mcp_list_pdfs() -> Dict[str, Any]:
    return call_tool_sync("list_pdfs", {})

def mcp_get_table_of_contents(path: str) -> Dict[str, Any]:
    """Chama a ferramenta que extrai o sumário de um PDF."""
    return call_tool_sync("get_table_of_contents", {"path": path})