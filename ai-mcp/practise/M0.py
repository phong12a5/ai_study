# server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("M0")          # tên server

@mcp.tool()                    # decorator -> SDK tự sinh JSON schema từ type hint + docstring
def cong_hai_so(a: int, b: int) -> int:
    """Cộng hai số và trả về tổng."""   # docstring = description cho LLM
    return a + b

if __name__ == "__main__":
    mcp.run()                  # mặc định chạy stdio