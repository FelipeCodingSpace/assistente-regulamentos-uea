
import asyncio
from fastmcp import Client
from typing import Any, Dict, Optional

# Path para o servidor MCP (relativo ao repositório)
MCP_SERVER_ENTRYPOINT = "mcp/pdf_server.py"

# Internals async client (reutilizável)
async def _call_tool_async(tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
    async with Client(MCP_SERVER_ENTRYPOINT) as client:
        # lista ferramentas disponíveis (opcional)
        # tools = await client.list_tools()
        res = await client.call_tool(tool, args)
        # res.content is a list; fastmcp returns content objects
        # A convenção aqui assume que tool retorna um dict serializável
        # fastmcp returns a structure where res.content[0].text contains JSON/string results sometimes
        # Para simplicidade, retornamos o primeiro content object as-is.
        try:
            content_obj = res.content[0]
            # fastmcp content objects can have .text attribute
            if hasattr(content_obj, "text"):
                return {"ok": True, "raw": content_obj.text}
            else:
                # fallback: return repr
                return {"ok": True, "raw": content_obj}
        except Exception as e:
            return {"ok": False, "error": str(e)}

def call_tool_sync(tool: str, args: Dict[str, Any], timeout: Optional[float] = 30.0) -> Dict[str, Any]:
    """
    Wrapper síncrono para chamar ferramentas MCP.
    """
    try:
        return asyncio.run(asyncio.wait_for(_call_tool_async(tool, args), timeout))
    except Exception as e:
        return {"ok": False, "error": str(e)}

# Conveniências
def mcp_list_pdfs(folder: str = "") -> Dict[str, Any]:
    return call_tool_sync("list_pdfs", {"folder": folder})

def mcp_read_pdf(path: str) -> Dict[str, Any]:
    return call_tool_sync("read_pdf", {"path": path})

def mcp_extract_page(path: str, page_number: int) -> Dict[str, Any]:
    return call_tool_sync("extract_page", {"path": path, "page_number": page_number})

def mcp_find_section(path: str, heading_keyword: str) -> Dict[str, Any]:
    return call_tool_sync("find_section_by_heading", {"path": path, "heading_keyword": heading_keyword})
