# MCP — Model Context Protocol (Lý thuyết + Bài tập)

> Mục tiêu: hiểu MCP là gì, vì sao nó tồn tại, và **tự viết một MCP server rồi cắm vào chính Claude Code** bạn đang dùng để thấy tool tự viết xuất hiện thật.
> Tiền đề: bạn đã tự viết tool (T0–T5) và agent (A1–Capstone). MCP là bước "chuẩn hóa" những tool đó.

---

# PHẦN I — LÝ THUYẾT

## 1. Vấn đề MCP giải quyết

Ở các bài trước, mỗi tool bạn phải tự: viết JSON schema + viết hàm + đăng ký `dispatch` — và nó **chỉ dùng được trong đúng app đó**. Muốn agent dùng GitHub, Slack, Postgres... mỗi app lại tích hợp lại từ đầu, mỗi nơi một kiểu.

```
KHÔNG MCP:  M app × N tool = M×N lần tích hợp (mỗi cặp viết tay)
CÓ MCP:     mỗi tool đóng gói 1 lần thành "server" → mọi app cắm vào dùng
            ⇒ M + N (cắm là chạy)
```

MCP (Model Context Protocol) là **chuẩn mở** do Anthropic công bố (11/2024) để kết nối ứng dụng AI với hệ thống/dữ liệu bên ngoài. Ví von: **"cổng USB-C cho AI"** — một chuẩn cắm chung.

> 🔑 MCP **không** phải khái niệm agent mới. Vòng lặp agent, tool calling vẫn y nguyên. MCP chỉ chuẩn hóa **cách tool/dữ liệu được cung cấp** cho agent, để tái sử dụng giữa nhiều app.

## 2. Kiến trúc: Host – Client – Server

```
┌─────────────────── HOST (vd: Claude Code, Claude Desktop) ───────────────────┐
│   ┌──────────┐        ┌──────────┐         ┌──────────┐                       │
│   │ Client A │◀──────▶│ Client B │◀───────▶│ Client C │   (mỗi client 1:1     │
│   └────┬─────┘        └────┬─────┘         └────┬─────┘    với một server)     │
└────────┼───────────────────┼────────────────────┼──────────────────────────────┘
         ▼                   ▼                     ▼
   ┌───────────┐       ┌───────────┐         ┌───────────┐
   │ Server:   │       │ Server:   │         │ Server:   │
   │ filesystem│       │ github    │         │ của-bạn   │
   └───────────┘       └───────────┘         └───────────┘
```

- **Host**: ứng dụng LLM người dùng chạy (Claude Code chính là một host). Chứa các **Client**.
- **Client**: cầu nối 1:1 tới một Server, nằm trong Host.
- **Server**: bên **cung cấp năng lực** (tool/dữ liệu/prompt). Đây là cái **bạn sẽ viết**.

## 3. Ba "primitive" một Server có thể cung cấp

| Primitive | Ai điều khiển | Là gì | Tương ứng đã học |
|---|---|---|---|
| **Tools** | Model (LLM tự gọi) | Hàm có side-effect/tính toán | Đúng tool use T0–T5 |
| **Resources** | App | Dữ liệu chỉ-đọc nạp vào context (file, record DB) | Giống "retrieval"/context |
| **Prompts** | Người dùng | Mẫu prompt tái dùng (vd slash command) | Template prompt |

> Phần lớn lúc đầu bạn chỉ cần **Tools**. Resources & Prompts là mở rộng.

## 4. Transport — server chạy ở đâu

- **stdio**: server là một tiến trình con chạy **cục bộ**, giao tiếp qua stdin/stdout. Đơn giản nhất, hợp để học & dùng cá nhân.
- **Streamable HTTP**: server chạy **từ xa** (web service), nhiều người/app dùng chung.

Buổi này ta dùng **stdio** (local) cho nhẹ.

## 5. So sánh: tool tự viết (T0–T5) vs MCP

| | Tool tự viết | MCP tool |
|---|---|---|
| LLM gọi hàm | ✅ | ✅ (y hệt) |
| Định nghĩa ở đâu | Trong app, schema viết tay | Trong server, SDK tự sinh schema từ type hint |
| Tái dùng giữa app | ❌ phải copy | ✅ cắm là chạy |
| Dùng được trong Claude Code | ❌ | ✅ |

---

# PHẦN II — BÀI TẬP

## Chuẩn bị
```bash
pip install "mcp[cli]"        # Python SDK (gồm FastMCP + công cụ dev)
# Tài liệu: https://modelcontextprotocol.io  và  https://github.com/modelcontextprotocol/python-sdk
```

FastMCP "hello world" — đọc kỹ mẫu này trước:
```python
# server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")          # tên server

@mcp.tool()                    # decorator -> SDK tự sinh JSON schema từ type hint + docstring
def cong_hai_so(a: int, b: int) -> int:
    """Cộng hai số và trả về tổng."""   # docstring = description cho LLM
    return a + b

if __name__ == "__main__":
    mcp.run()                  # mặc định chạy stdio
```

> 💡 Khác biệt lớn so với T0–T5: bạn **không viết JSON schema tay nữa**. SDK đọc type hint (`a: int`) + docstring để tự sinh. Type hint giờ là "tài liệu cho LLM".

---

## Bài M0 — Hello MCP server
**Mục tiêu:** dựng và soi được một server tối thiểu.

**Đề:** Viết `server.py` như mẫu trên với tool `cong_hai_so`. Dùng công cụ dev của MCP để kiểm tra:
```bash
mcp dev server.py        # mở MCP Inspector (giao diện web) để gọi thử tool
```
Gọi thử tool trong Inspector, xác nhận trả về đúng tổng.

**Đạt khi:** Inspector liệt kê tool `cong_hai_so` với schema đúng (a, b) và gọi ra kết quả.

---

## Bài M1 — Đóng gói tool đã có thành server
**Mục tiêu:** chuyển tool tự viết từ module agent sang MCP.

**Đề:** Tạo `country_server.py` expose 2 tool tái dùng từ bài agent:
- `tra_cuu(country: str) -> str` — thông tin quốc gia (mock VN/Nhật như cũ)
- `doi_tien(amount: float, from_cur: str, to_cur: str) -> float`

Nhớ viết **docstring rõ ràng** cho mỗi tool (đó là description LLM đọc).

**Gợi ý:** copy logic hàm từ `ai-agent/practise/`, bỏ phần JSON schema tay — chỉ cần type hint + docstring.

**Đạt khi:** `mcp dev country_server.py` hiện đủ 2 tool, gọi thử ra kết quả đúng.

---

## Bài M2 — Cắm server vào Claude Code thật 🎯
**Mục tiêu:** thấy tool tự viết xuất hiện trong chính Claude Code.

**Đề:** Đăng ký `country_server.py` làm MCP server cho Claude Code:
```bash
# Trong thư mục dự án:
claude mcp add country -- python /đường/dẫn/tuyệt/đối/country_server.py
claude mcp list            # kiểm tra đã thêm
```
Mở Claude Code, hỏi: *"Tra cứu thủ đô Nhật Bản giúp tôi"* và xem nó **gọi tool của bạn**.

**Gợi ý:** dùng đường dẫn tuyệt đối + đúng python của venv. Gõ `claude mcp --help` nếu cú pháp khác phiên bản. Trong phiên Claude Code, dùng `/mcp` để xem trạng thái server.

**Đạt khi:** Claude Code gọi `tra_cuu` của bạn và trả lời dựa trên kết quả đó (không phải kiến thức có sẵn).

---

## Bài M3 — Thêm một Resource
**Mục tiêu:** phân biệt Tool (model gọi) vs Resource (app nạp dữ liệu).

**Đề:** Thêm vào server một resource liệt kê danh sách quốc gia hỗ trợ:
```python
@mcp.resource("countries://list")
def danh_sach_quoc_gia() -> str:
    """Danh sách quốc gia được hỗ trợ tra cứu."""
    return "Việt Nam, Nhật Bản"
```
Soi nó trong Inspector / `/mcp` của Claude Code.

**Đạt khi:** Resource `countries://list` hiện ra và đọc được nội dung.

---

## Bài M4 — Thêm một Prompt
**Mục tiêu:** tạo mẫu prompt tái dùng (giống slash command).

**Đề:** Thêm một prompt template:
```python
@mcp.prompt()
def so_sanh(q1: str, q2: str) -> str:
    """Tạo prompt so sánh 2 quốc gia."""
    return f"Hãy so sánh {q1} và {q2} về thủ đô và dân số, trình bày bảng."
```
Gọi nó từ Claude Code (qua menu prompt/`/mcp`).

**Đạt khi:** Prompt `so_sanh` dùng được, sinh ra câu so sánh đúng định dạng.

---

## Bài M5 (nâng cao) — Viết MCP Client bằng Python
**Mục tiêu:** hiểu cả ĐẦU CÒN LẠI — không chỉ server.

**Đề:** Dùng `mcp` client SDK viết một script Python: khởi chạy `country_server.py` qua stdio, **liệt kê tool**, rồi **gọi `tra_cuu("Việt Nam")`** và in kết quả — không qua Claude Code.

**Gợi ý:** xem mẫu client trong README của python-sdk (dùng `ClientSession` + `stdio_client`). Đây là cách Claude Code "nói chuyện" với server bạn ở mức thấp.

**Đạt khi:** Script tự kết nối server, list được tool và nhận đúng kết quả `tra_cuu`.

---

## Capstone MCP — Server "country-info" hoàn chỉnh 🎓
**Mục tiêu:** gói mọi thứ thành một server dùng được thật.

**Đề:** Hoàn thiện `country_server.py` gồm:
1. **Tools**: `tra_cuu`, `doi_tien`, `cong_hai_so` (docstring + type hint chuẩn).
2. **Resource**: `countries://list`.
3. **Prompt**: `so_sanh`.
4. Cắm vào Claude Code (M2) và chứng minh dùng được cả 3 primitive.

**Kịch bản kiểm thử trong Claude Code:** *"So sánh dân số Việt Nam và Nhật Bản, rồi tính tổng."* → phải thấy nó gọi `tra_cuu` (×2) + `cong_hai_so` của server bạn.

**Đạt khi:** chạy end-to-end trong Claude Code, cả tool/resource/prompt đều hoạt động.

---

## Tự kiểm tra
1. M×N vs M+N — MCP cải thiện điều gì?
2. Host / Client / Server: Claude Code là cái nào? Cái bạn viết là cái nào?
3. Tool, Resource, Prompt khác nhau ở "ai điều khiển"?
4. Vì sao với MCP bạn không cần viết JSON schema tay nữa?
5. stdio khác Streamable HTTP ở điểm nào?

---

## Checklist
- [ ] M0 — Hello MCP server
- [ ] M1 — Đóng gói tool đã có
- [ ] M2 — Cắm vào Claude Code 🎯
- [ ] M3 — Resource
- [ ] M4 — Prompt
- [ ] M5 — MCP Client bằng Python
- [ ] Capstone — Server country-info hoàn chỉnh

> Xong Capstone: bạn đã đi từ **Workflow → Tool Use → Agent → MCP** — tức tự viết được tool, agent, và đóng gói tool theo chuẩn ngành dùng chung với Claude Code.
> Bước sau (tùy chọn): **RAG** (trí nhớ dài hạn + retrieval) hoặc **LangGraph** (dựng lại agent bằng framework).
