# Bài tập Tool Use — Thực hành

> Làm theo thứ tự. Các bài T0→T3 dẫn bạn từ "gọi 1 tool" đến "vòng lặp agent đầu tiên".
> Dùng client OpenAI trực tiếp (vì cần đọc `tool_calls` — hàm `llm()` cũ chỉ trả text nên không đủ).

## Chuẩn bị

```python
import json
from openai import OpenAI
client = OpenAI()
MODEL = "gpt-4o"     # tool use cần model hỗ trợ function calling
```

---

## Bài T0 — Một tool, gọi 2 lần (Workflow)
**Mục tiêu:** chạy đúng cơ chế 4 bước với 1 tool.

**Đề:** Tạo tool `cong_hai_so(a, b)` (cộng 2 số). Hỏi LLM: *"12345 cộng 67890 bằng bao nhiêu?"*. Bắt LLM gọi tool, bạn chạy hàm thật, trả kết quả, LLM đọc kết quả và trả lời bằng câu hoàn chỉnh.

**Gợi ý:** Viết tool schema với `parameters` gồm `a`, `b` kiểu `"number"`. In ra `msg.tool_calls` để xem LLM gọi gì.

**Đạt khi:** LLM trả về đúng 80235 và câu trả lời tự nhiên (không tự bịa số khi chưa gọi tool).

---

## Bài T1 — Trích xuất tham số
**Mục tiêu:** thấy LLM tự bóc tham số từ câu nói tự nhiên.

**Đề:** Tool `get_weather(city)` (mock: trả chuỗi cố định theo thành phố). Hỏi bằng nhiều câu khác nhau: *"Tokyo nóng không?"*, *"Cho mình xem thời tiết Đà Nẵng"*. Kiểm tra LLM bóc đúng `city`.

**Đạt khi:** Với cả 2 câu, `tool_calls` chứa đúng tên thành phố tương ứng.

---

## Bài T2 — Nhiều tool, LLM tự chọn
**Mục tiêu:** LLM định tuyến đến đúng tool (giống Routing nhưng do LLM quyết qua tool).

**Đề:** Cung cấp 3 tool cùng lúc:
- `get_weather(city)` — thời tiết
- `cong_hai_so(a, b)` — cộng số
- `doi_tien(amount, from_cur, to_cur)` — đổi tiền (mock tỉ giá cố định)

Hỏi 3 câu khác loại. Kiểm tra mỗi câu LLM chọn đúng tool. Thử 1 câu **không cần tool nào** (vd "Chào bạn") → LLM phải trả lời text, không gọi tool.

**Đạt khi:** 3 câu route đúng tool, 1 câu chào không gọi tool.

---

## Bài T3 — Vòng lặp Agent đầu tiên 🎯
**Mục tiêu:** bọc tool call trong `while` → tạo agent tự quyết nhiều bước.

**Đề:** Dùng các tool ở T2. Viết hàm `agent(user_input, max_steps=10)` theo mẫu mục 4 trong tài liệu. Đặt câu **cần nhiều tool nối tiếp**, ví dụ:

> *"Đổi 100 USD sang VND, rồi cộng thêm 50000 vào kết quả đó."*

LLM phải: gọi `doi_tien` → nhận kết quả → gọi `cong_hai_so` với kết quả đó → trả lời. In log mỗi bước (LLM gọi tool gì, kết quả gì).

**Đạt khi:** Agent tự thực hiện ≥2 lần gọi tool nối tiếp mà bạn KHÔNG hard-code thứ tự; log cho thấy rõ chuỗi suy luận.

---

## Bài T4 — Xử lý lỗi tool
**Mục tiêu:** tool fail nhưng agent không chết.

**Đề:** Sửa `doi_tien` để **raise lỗi** nếu `from_cur` không hỗ trợ (vd "XYZ"). Trong vòng agent, bọc `try/except`, trả thông báo lỗi **về cho LLM** (dạng string trong `role: tool`). Hỏi câu có đơn vị tiền lạ → quan sát LLM tự xin lỗi/hỏi lại thay vì crash.

**Đạt khi:** Chương trình không crash; LLM phản hồi hợp lý về việc không đổi được loại tiền đó.

---

## Bài T5 (nâng cao) — Mini ReAct Agent
**Mục tiêu:** ghép tool use + suy luận thành agent giải bài thật.

**Đề:** Thêm tool `tra_cuu(keyword)` (mock: trả vài "dữ kiện" cố định, vd dân số/diện tích vài nước). Hỏi câu cần **tra cứu nhiều lần rồi tính toán**, ví dụ:

> *"Tổng dân số của Việt Nam và Nhật Bản là bao nhiêu?"*

Agent phải: tra Việt Nam → tra Nhật Bản → cộng → trả lời. In log từng bước "nghĩ → gọi tool → quan sát".

**Đạt khi:** Agent tự chuỗi: 2 lần `tra_cuu` + 1 lần cộng + trả lời đúng tổng.

---

## Checklist

- [ ] T0 — Một tool, 2 lần gọi
- [ ] T1 — Trích xuất tham số
- [ ] T2 — Nhiều tool, LLM tự chọn
- [ ] T3 — Vòng lặp agent đầu tiên 🎯
- [ ] T4 — Xử lý lỗi tool
- [ ] T5 — Mini ReAct agent

> Hoàn thành T3 = bạn đã viết Agent đầu tiên. Hoàn thành T5 = bạn đã sẵn sàng cho buổi **Agent chuyên sâu**
> (ReAct, memory, multi-agent, đánh giá agent). Lời giải mẫu T3 ở `solutions/tool_use_agent.py`.
