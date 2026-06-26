"""Capstone MCP — Server "country-info" hoàn chỉnh (Tools + Resource + Prompt).

Cài đặt:  pip install "mcp[cli]"
Soi thử:  mcp dev solutions/country_server.py        (mở MCP Inspector)
Cắm vào Claude Code:
    claude mcp add country -- python /đường/dẫn/tuyệt/đối/country_server.py
    claude mcp list
    # trong phiên Claude Code: gõ /mcp để xem trạng thái

Điểm khác T0-T5: KHÔNG viết JSON schema tay nữa — FastMCP tự sinh schema
từ type hint + docstring. Vậy nên type hint & docstring giờ chính là "tài liệu cho LLM".
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("country-info")

# Dữ liệu mock (thay bằng DB/API thật khi cần)
_COUNTRIES = {
    "Việt Nam": {"thu_do": "Hà Nội", "dan_so_trieu": 97},
    "Nhật Bản": {"thu_do": "Tokyo", "dan_so_trieu": 126},
}
# Tỉ giá mock so với USD (1 USD = ? đơn vị)
_RATES = {"USD": 1.0, "VND": 25000.0, "EUR": 0.92, "JPY": 155.0}


# ---------------- TOOLS (model tự gọi) ----------------
@mcp.tool()
def tra_cuu(country: str) -> str:
    """Tra cứu thủ đô và dân số của một quốc gia. Hỗ trợ: 'Việt Nam', 'Nhật Bản'."""
    info = _COUNTRIES.get(country)
    if info is None:
        return f"Không tìm thấy thông tin về '{country}'."
    return f"Thủ đô: {info['thu_do']}, Dân số: {info['dan_so_trieu']} triệu"


@mcp.tool()
def cong_hai_so(a: float, b: float) -> float:
    """Cộng hai số và trả về tổng."""
    return a + b


@mcp.tool()
def doi_tien(amount: float, from_cur: str, to_cur: str) -> str:
    """Đổi tiền giữa hai loại tiền tệ. Hỗ trợ: USD, VND, EUR, JPY."""
    f, t = from_cur.upper(), to_cur.upper()
    if f not in _RATES or t not in _RATES:
        return f"Không hỗ trợ đổi {from_cur} -> {to_cur}. Chỉ có: {', '.join(_RATES)}."
    ket_qua = amount / _RATES[f] * _RATES[t]      # quy về USD rồi sang tiền đích
    return f"{amount} {f} = {ket_qua:,.2f} {t}"


# ---------------- RESOURCE (app nạp vào context, chỉ-đọc) ----------------
@mcp.resource("countries://list")
def danh_sach_quoc_gia() -> str:
    """Danh sách quốc gia được hỗ trợ tra cứu."""
    return ", ".join(_COUNTRIES.keys())


# ---------------- PROMPT (mẫu prompt người dùng kích hoạt) ----------------
@mcp.prompt()
def so_sanh(q1: str, q2: str) -> str:
    """Tạo prompt so sánh hai quốc gia về thủ đô và dân số."""
    return (
        f"Hãy tra cứu rồi so sánh {q1} và {q2} về thủ đô và dân số. "
        "Trình bày kết quả dưới dạng bảng, sau đó tính tổng dân số hai nước."
    )


if __name__ == "__main__":
    mcp.run()        # mặc định transport = stdio
