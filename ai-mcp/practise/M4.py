# country_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("M1")          # tên server

@mcp.tool()
def tra_cuu(country):
    """ Tra cứu thông tin: Thủ đô, Dân số của quốc gia được yêu cầu """
    # This is a mock implementation - replace with actual country lookup
    country_info = {
        "Việt Nam": "Thủ đô: Hà Nội, Dân số: 97 triệu",
        "Nhật Bản": "Thủ đô: Tokyo, Dân số: 126 triệu"
    }
    return country_info.get(country, "Không tìm thấy thông tin về quốc gia này.")

@mcp.resource("countries://list")
def danh_sach_quoc_gia() -> str:
    """Danh sách quốc gia được hỗ trợ tra cứu."""
    return "Việt Nam, Nhật Bản"
    
@mcp.prompt()
def so_sanh(q1: str, q2: str) -> str:
    """Tạo prompt so sánh 2 quốc gia."""
    return f"Hãy so sánh {q1} và {q2} về thủ đô và dân số, trình bày bảng."
    
@mcp.tool()
def doi_tien(amount: float, from_cur, to_cur):
    """ Công cụ chuyển đổi tiền tệ """
    mock_exchange_rate = 0.85  # Mock exchange rate for demonstration
    converted_amount = amount * mock_exchange_rate
    return converted_amount

if __name__ == "__main__":
    mcp.run()                  # mặc định chạy stdio