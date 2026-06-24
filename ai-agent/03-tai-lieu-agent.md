# Agent Chuyên Sâu — Từ vòng lặp tới hệ thống agent thật

> Bạn đã viết được agentic loop (T3–T5). Buổi này biến nó thành **agent dùng được thật**: tái sử dụng, có tính cách, có trí nhớ, có rào chắn an toàn, biết phối hợp nhiều agent, và **đo lường được**.

---

## 0. Bản đồ buổi học

```
Vòng lặp rời rạc (T3-T5)
   │
   ├─ 1. Gom thành LỚP Agent tái sử dụng        ← nền tảng
   ├─ 2. System prompt: cho agent vai trò & luật
   ├─ 3. ReAct: bắt agent "nghĩ trước khi làm"
   ├─ 4. Memory: nhớ qua nhiều lượt / dài hạn
   ├─ 5. Guardrails: dừng đúng lúc, an toàn
   ├─ 6. Multi-agent: nhiều agent phối hợp
   └─ 7. Evaluation: làm sao biết agent TỐT?
```

---

## 1. Gom thành lớp Agent tái sử dụng

Ở T2–T5 bạn copy `tools` + `dispatch` + vòng lặp qua từng file. Giờ gom lại thành **một class** nhận `tools`, `dispatch`, `system` làm tham số. Bản chuẩn (`solutions/agent_class.py`) sửa luôn 3 lỗi tiềm ẩn:

| Lỗi ở bài T | Sửa trong class |
|---|---|
| Tool lạ không được append tool message → lỗi 400 | **Mọi** `tool_call` đều trả về một tool message, kể cả khi lỗi/không tồn tại |
| `except ValueError` quá hẹp | `except Exception` — bắt mọi lỗi, đẩy về LLM |
| `agent()` trả `None` | `run()` trả `content`; hết `max_steps` trả fallback |

Ý tưởng cốt lõi — một hàm `_run_tool()` **không bao giờ raise**, luôn trả string (kết quả hoặc thông báo lỗi):

```python
def _run_tool(self, tool_call):
    name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        return f"LỖI: tham số JSON không hợp lệ ({e})"
    fn = self.dispatch.get(name)
    if fn is None:
        return f"LỖI: tool '{name}' không tồn tại."     # ← vẫn trả message, không im lặng
    try:
        return str(fn(**args))
    except Exception as e:
        return f"LỖI khi chạy {name}: {e}"               # ← mọi lỗi -> đẩy về LLM
```

> 🔑 Nguyên tắc vàng của agent: **tool không bao giờ được làm sập vòng lặp**. Lỗi là dữ liệu để LLM tự xử lý, không phải exception để chương trình chết.

---

## 2. System prompt — cho agent vai trò & luật chơi

Đến giờ agent của bạn "vô hồn". `system` prompt định nghĩa:
- **Vai trò**: "Bạn là trợ lý tài chính cá nhân."
- **Quy tắc**: "Luôn dùng tool để tính toán, không tự nhẩm. Trả lời bằng tiếng Việt."
- **Giới hạn**: "Nếu không có tool phù hợp, nói rõ là không làm được."

```python
agent = Agent(
    tools=tools, dispatch=dispatch,
    system="Bạn là trợ lý toán học. LUÔN dùng tool để tính, không tự tính nhẩm. "
           "Nếu thiếu dữ kiện, hãy hỏi lại người dùng."
)
```

System prompt là **đòn bẩy rẻ nhất** để định hình hành vi agent. Chỉnh nó trước khi nghĩ tới giải pháp phức tạp.

---

## 3. ReAct — "Reason + Act" (nghĩ rồi làm)

ReAct là pattern: trước mỗi hành động, bắt LLM **viết ra suy luận** ("tôi cần làm gì, tại sao") rồi mới gọi tool. Lợi ích: agent ít đi sai hướng, và bạn **debug được** vì thấy nó "nghĩ" gì.

Có 2 cách:
- **Ngầm**: model mạnh (gpt-4o, claude) tự suy luận khi gọi tool — bạn thấy qua thứ tự tool call (T5 chính là ReAct ngầm).
- **Tường minh**: thêm vào system prompt yêu cầu "Trước mỗi bước, ghi 'Suy nghĩ: ...' rồi mới hành động", hoặc thêm tool `think(thought)` để model ghi lại lập luận.

```python
system = ("Hãy giải quyết từng bước. Trước khi gọi tool, giải thích ngắn gọn "
          "vì sao bạn chọn tool đó. Sau khi có đủ thông tin mới đưa kết luận cuối.")
```

> 💡 Vòng lặp agent của bạn ĐÃ là ReAct: "Reason" = LLM quyết tool, "Act" = chạy tool, "Observation" = kết quả trả về. ReAct chỉ làm bước Reason hiện rõ hơn.

---

## 4. Memory — trí nhớ

Có 2 loại, đừng nhầm:

**a) Trí nhớ ngắn hạn (working memory) = lịch sử hội thoại.**
Chính là `self.messages`. Nếu bạn **giữ lại `messages` qua nhiều lần `run()`**, agent nhớ được lượt trước:

```
run("Tên tôi là Phong")        -> "Chào Phong!"
run("Tôi tên gì?")             -> "Bạn tên Phong."   ← nhớ vì messages được giữ
```

Giới hạn: context window có hạn. Hội thoại dài → phải **tóm tắt** bớt (summary) hoặc cắt bớt lượt cũ.

**b) Trí nhớ dài hạn (long-term memory).**
Khi cần nhớ qua nhiều phiên / khối lượng lớn: lưu ra ngoài (file, DB, **vector store**) rồi **truy xuất** (retrieval) đoạn liên quan nhét vào prompt khi cần. Đây là cầu nối sang RAG.

```
       ┌─────────────┐   lưu    ┌──────────────┐
       │   Agent     │ ───────▶ │ Vector store │
       │  (run này)  │ ◀─────── │  (DB ngoài)  │
       └─────────────┘ truy xuất└──────────────┘
         (nhớ cả phiên trước)
```

> Quy tắc: dùng trí nhớ ngắn hạn (messages) trước. Chỉ thêm vector memory khi thực sự cần nhớ vượt một phiên.

---

## 5. Guardrails — dừng đúng lúc & an toàn

Agent tự quyết ⇒ phải có rào chắn, nếu không nó có thể lặp vô tận hoặc làm việc nguy hiểm.

| Rào chắn | Vì sao | Cách làm |
|---|---|---|
| **`max_steps`** | chống lặp vô tận, đốt tiền | đã có trong class |
| **Giới hạn chi phí/thời gian** | bảo vệ ví & UX | đếm token / đặt timeout |
| **Human-in-the-loop** | tool nguy hiểm (xóa, gửi tiền, chạy shell) | hỏi xác nhận trước khi thực thi |
| **Validate đầu ra tool** | LLM sinh args sai | kiểm tra kiểu/range trước khi chạy |
| **Allowlist tool** | giới hạn quyền agent | chỉ đưa tool thật sự cần |

Ví dụ human-in-the-loop:
```python
DANGEROUS = {"xoa_file", "gui_tien"}
if name in DANGEROUS:
    if input(f"Cho phép chạy {name}({args})? [y/N] ").lower() != "y":
        return "Người dùng từ chối thao tác này."
```

---

## 6. Multi-agent — nhiều agent phối hợp

Khi một agent ôm quá nhiều việc (quá nhiều tool, system prompt quá dài), tách thành nhiều agent chuyên biệt do một **orchestrator** điều phối:

```
                  ┌──▶ [Research Agent]  (có tool tra cứu)
[Orchestrator] ───┼──▶ [Coder Agent]     (có tool chạy code)
   (điều phối)    └──▶ [Writer Agent]    (chỉ viết)
        │
        └──▶ tổng hợp kết quả -> trả người dùng
```

Cách hiện thực đơn giản: **một sub-agent chính là một tool của orchestrator**. Orchestrator gọi tool `research_agent(query)` — bên trong tool đó là một `Agent` khác chạy độc lập.

> ⚠️ Cảnh báo thực chiến: multi-agent **đắt và khó debug hơn nhiều**. Đừng dùng khi một agent + system prompt tốt là đủ. Chỉ tách khi các vai trò thực sự khác nhau và xung đột nếu nhét chung.

---

## 7. Evaluation — làm sao biết agent TỐT?

Đây là phần **bị bỏ quên nhiều nhất** nhưng quan trọng nhất khi lên production. Agent khó đánh giá vì có nhiều đường đi tới đáp án. Ba tầng đo:

1. **Task success (kết quả cuối)** — agent có ra đúng đáp án không? Cần bộ test case có đáp án kỳ vọng.
2. **Trajectory (đường đi)** — agent có gọi đúng/đủ tool, không vòng vo, không tốn bước thừa?
3. **LLM-as-judge** — dùng một LLM khác chấm chất lượng câu trả lời theo tiêu chí (bạn đã làm ở Evaluator–Optimizer buổi workflow!).

Khung eval tối thiểu:
```python
test_cases = [
    {"input": "Tổng dân số VN và Nhật?", "expect_contains": "223"},
    {"input": "Đổi 100 USD sang VND",     "expect_tool": "doi_tien"},
]
for tc in test_cases:
    out = agent.run(tc["input"])
    passed = tc["expect_contains"] in out
    print("PASS" if passed else "FAIL", tc["input"])
```

> 💡 Không có eval, bạn không biết một thay đổi prompt làm agent tốt lên hay tệ đi. **Luôn xây eval trước khi tối ưu.**

---

## 8. Khi nào tự viết, khi nào dùng framework?

| | Tự viết (như bạn đang làm) | Framework (LangGraph, ...) |
|---|---|---|
| Hiểu cơ chế | ✅ Sâu | 🟡 Bị che bớt |
| Tốc độ dựng | 🟡 Chậm hơn | ✅ Nhanh |
| State/checkpoint/streaming phức tạp | 🟡 Tự lo | ✅ Có sẵn |
| Debug | ✅ Dễ (code của bạn) | 🟡 Phải hiểu framework |

**Lời khuyên:** bạn đã hiểu cơ chế (tốt!). Khi bài toán cần state phức tạp, resume, nhiều nhánh — hãy thử LangGraph; lúc đó bạn map được "node = bước, edge = luồng, cycle = loop tôi từng tự viết".

---

## 9. Tự kiểm tra

1. Vì sao tool tuyệt đối không nên raise ra ngoài vòng lặp?
2. Trí nhớ ngắn hạn và dài hạn khác nhau chỗ nào? Khi nào cần loại 2?
3. Một sub-agent được "biến thành" gì trong kiến trúc multi-agent?
4. 3 tầng đánh giá agent là gì?
5. Khi nào KHÔNG nên dùng multi-agent?

> Làm bài tập trong `04-bai-tap-agent.md`. Bản giải nền tảng: `solutions/agent_class.py`.
