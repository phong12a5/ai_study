# Bài tập Agent Chuyên Sâu

> Tiếp nối T0–T5. Mỗi bài xây trên bài trước. Bản giải nền: `solutions/agent_class.py`.
> Khuyến nghị: làm A1 trước (lớp Agent tái sử dụng) rồi các bài sau đều dùng lại nó.

## Chuẩn bị
```python
from openai import OpenAI   # vẫn dùng OpenAI function calling như T0-T5
```

---

## Bài A1 — Lớp Agent tái sử dụng 🧱
**Mục tiêu:** gom vòng lặp T3–T5 thành một class, sửa 3 lỗi tiềm ẩn.

**Đề:** Viết `class Agent` nhận `tools`, `dispatch`, `system`, `model`, `max_steps`. Có method `run(user_input)` trả về câu trả lời cuối. Yêu cầu bắt buộc:
1. **Mọi** `tool_call` đều được append một tool message (kể cả tool lạ / lỗi).
2. Bắt `except Exception` (không chỉ `ValueError`), đẩy lỗi về LLM dạng string.
3. `run()` **trả về** kết quả; hết `max_steps` trả thông báo fallback.

Test lại bằng câu của T3 và T5 → phải ra kết quả như cũ.

**Đạt khi:** chạy được T3 + T5 qua class; thử thêm tool lạ (sửa LLM gọi sai tên) không còn lỗi 400.

---

## Bài A2 — System prompt & persona
**Mục tiêu:** thấy system prompt đổi hành vi agent.

**Đề:** Dùng `Agent` ở A1, tạo 2 agent khác persona **trên cùng bộ tool**:
- `math_agent`: "LUÔN dùng tool để tính, không tự nhẩm. Trả lời ngắn gọn."
- `friendly_agent`: "Trả lời vui vẻ, thêm emoji, giải thích từng bước cho người mới."

Hỏi cùng một câu cho cả hai, so sánh phản hồi.

**Đạt khi:** Hai agent trả lời khác phong cách rõ rệt dù cùng tool/cùng câu hỏi.

---

## Bài A3 — Memory đa lượt (hội thoại)
**Mục tiêu:** agent nhớ ngữ cảnh qua nhiều lượt.

**Đề:** Giữ `self.messages` qua nhiều lần `run()`. Tạo vòng chat:
```
Bạn: Tên tôi là Phong, tôi có 100 USD.
Bạn: Đổi hết sang VND giúp tôi.     # agent phải nhớ "100 USD"
Bạn: Tôi tên gì?                     # agent phải nhớ "Phong"
```

**Gợi ý:** thêm method `chat()` đọc input liên tục, hoặc gọi `run()` nhiều lần trên cùng instance.

**Đạt khi:** agent trả lời đúng dựa trên thông tin của các lượt TRƯỚC (không hỏi lại).

---

## Bài A4 — Guardrails (human-in-the-loop)
**Mục tiêu:** chặn thao tác nguy hiểm trước khi chạy.

**Đề:** Thêm tool `gui_tien(amount, to_account)` (mock). Đánh dấu nó là "nguy hiểm": trước khi thực thi, agent phải **hỏi xác nhận** người dùng (`input()` y/N). Nếu từ chối → trả "Người dùng từ chối" về LLM.

Thử 1 câu khiến agent muốn gửi tiền → quan sát bước xác nhận. Bấm N → agent xử lý lịch sự.

**Đạt khi:** tool nguy hiểm không bao giờ chạy nếu chưa được xác nhận; tool thường vẫn chạy bình thường.

---

## Bài A5 — ReAct tường minh
**Mục tiêu:** làm bước suy luận hiện rõ để debug.

**Đề:** Thêm vào system prompt yêu cầu: trước mỗi hành động, ghi "Suy nghĩ: ..." giải thích vì sao chọn tool. Chạy lại bài T5 (tổng dân số) và in ra cả phần suy nghĩ của agent ở mỗi bước.

**Đạt khi:** log cho thấy chuỗi "Suy nghĩ → gọi tool → quan sát" rõ ràng cho từng bước.

---

## Bài A6 — Multi-agent 🤝
**Mục tiêu:** một orchestrator điều phối nhiều sub-agent.

**Đề:** Tạo 2 sub-agent chuyên biệt:
- `research_agent`: chỉ có tool `tra_cuu` (như T5).
- `math_agent`: chỉ có tool `cong_hai_so`.

Biến **mỗi sub-agent thành một tool** của `orchestrator`:
- tool `nghien_cuu(query)` → bên trong gọi `research_agent.run(query)`
- tool `tinh_toan(query)` → bên trong gọi `math_agent.run(query)`

Hỏi orchestrator câu của T5. Nó phải tự điều phối: nhờ research lấy dữ liệu → nhờ math cộng → trả lời.

**Đạt khi:** orchestrator giải đúng bài bằng cách gọi sub-agent, không tự ôm hết tool.

---

## Bài A7 — Đánh giá agent (Evaluation)
**Mục tiêu:** đo chất lượng agent một cách có hệ thống.

**Đề:** Viết một eval harness chạy agent (A1) trên ≥4 test case, kiểm 2 tiêu chí:
- **Task success**: output có chứa đáp án kỳ vọng (`expect_contains`).
- **Trajectory**: agent có gọi đúng tool kỳ vọng (`expect_tool`) không.

In bảng PASS/FAIL + tỉ lệ đậu.

**Gợi ý:** cho `Agent` ghi lại danh sách tool đã gọi (vd `self.tool_log`) để kiểm trajectory.

**Đạt khi:** harness chạy tự động, báo cáo rõ bài nào fail và vì sao.

---

## Capstone — Research Assistant Agent 🎓
**Mục tiêu:** ghép tất cả thành một agent hoàn chỉnh.

**Đề:** Xây "Trợ lý nghiên cứu" với:
1. **System prompt** rõ vai trò + ReAct (A2, A5).
2. **Tools**: `tra_cuu`, `cong_hai_so`, và `tom_tat(text)` (tóm tắt).
3. **Memory** đa lượt (A3) để hỏi nối tiếp.
4. **Guardrail** `max_steps` + ít nhất 1 tool cần xác nhận (A4).
5. **Eval** 3 test case (A7) chứng minh nó hoạt động.

Kịch bản mẫu: "So sánh dân số VN và Nhật, rồi tóm tắt kết quả trong 1 câu."

**Đạt khi:** chạy end-to-end, log minh bạch từng bước, eval pass.

---

## Checklist
- [ ] A1 — Lớp Agent tái sử dụng 🧱
- [ ] A2 — System prompt & persona
- [ ] A3 — Memory đa lượt
- [ ] A4 — Guardrails (human-in-the-loop)
- [ ] A5 — ReAct tường minh
- [ ] A6 — Multi-agent 🤝
- [ ] A7 — Evaluation
- [ ] Capstone — Research Assistant

> Xong Capstone là bạn đã đi trọn: **Workflow → Tool Use → Agent → Multi-agent → Evaluation.**
> Bước sau (tùy chọn): RAG (trí nhớ dài hạn + truy xuất), hoặc dựng lại mọi thứ bằng LangGraph để so sánh.
