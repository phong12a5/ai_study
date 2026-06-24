# Tool Use (Function Calling) — Cây cầu từ Workflow sang Agent

> Mục tiêu: hiểu **cho LLM tự gọi hàm/công cụ** như thế nào. Đây là mảnh ghép cuối của "Augmented LLM" và là **nền tảng của mọi Agent**.

---

## 0. Tại sao cần Tool Use?

Đến giờ, LLM trong các bài của bạn chỉ làm một việc: **nhận text → sinh text**. Nhưng LLM có 2 giới hạn lớn:

1. **Không biết dữ liệu thời gian thực** (thời tiết, giá cổ phiếu, nội dung database của bạn).
2. **Tính toán/logic chính xác kém** (toán nhiều chữ số, gọi API, chạy code).

**Tool Use** giải quyết điều này: bạn cung cấp cho LLM một danh sách "công cụ" (hàm). LLM **tự quyết** khi nào cần gọi công cụ nào và với tham số gì. Bạn chạy hàm thật, trả kết quả về, LLM dùng kết quả để trả lời.

```
User: "Thời tiết Hà Nội hôm nay thế nào?"
  │
  ▼
LLM nghĩ: "Mình không biết, cần gọi tool get_weather(city='Hà Nội')"
  │
  ▼
CODE của bạn: chạy get_weather('Hà Nội') -> "28°C, nắng"
  │
  ▼
LLM nhận kết quả -> trả lời: "Hà Nội hôm nay 28°C, trời nắng."
```

> 🔑 Điểm mấu chốt: **LLM không tự chạy hàm**. Nó chỉ *nói cho bạn biết nó muốn gọi hàm nào với tham số gì*. **Bạn (code) là người thực thi** rồi đưa kết quả lại. Đây là ranh giới an toàn quan trọng.

---

## 1. Cơ chế 4 bước (rất quan trọng — học thuộc)

```
┌──────────────────────────────────────────────────────────────┐
│ 1. ĐỊNH NGHĨA TOOL  → mô tả hàm bằng JSON schema (tên, mô tả,  │
│                       tham số) và gửi kèm cho LLM              │
│                                                                │
│ 2. LLM QUYẾT ĐỊNH   → LLM trả về "tool_call": tên hàm + args   │
│                       (dạng JSON) — HOẶC trả lời text bình     │
│                       thường nếu không cần tool                │
│                                                                │
│ 3. CODE THỰC THI    → bạn parse args, gọi hàm Python thật,     │
│                       lấy kết quả                              │
│                                                                │
│ 4. TRẢ KẾT QUẢ LẠI  → append kết quả vào hội thoại, gọi LLM    │
│                       lần nữa để nó sinh câu trả lời cuối      │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Định nghĩa một tool (JSON Schema)

Tool được mô tả bằng schema. **Phần `description` cực kỳ quan trọng** — LLM dựa vào đó để quyết khi nào dùng tool. Viết mô tả rõ như viết tài liệu cho đồng nghiệp:

```python
get_weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Lấy thời tiết hiện tại của một thành phố. Dùng khi user hỏi về thời tiết.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Tên thành phố, ví dụ: 'Hà Nội', 'Tokyo'"
                }
            },
            "required": ["city"]
        }
    }
}
```

> ⚠️ Tool dở thường KHÔNG phải lỗi LLM — mà do **mô tả tool mơ hồ** hoặc **tham số không rõ**. Đầu tư vào description và tên tham số dễ hiểu.

---

## 3. Vòng gọi tool với OpenAI (bạn đang dùng OpenAI)

```python
import json
from openai import OpenAI
client = OpenAI()

# Hàm Python thật (mock cho dễ test)
def get_weather(city):
    fake = {"Hà Nội": "28°C, nắng", "Tokyo": "15°C, mưa nhẹ"}
    return fake.get(city, "Không có dữ liệu")

dispatch = {"get_weather": get_weather}   # map tên tool -> hàm thật
tools = [get_weather_tool]

messages = [{"role": "user", "content": "Thời tiết Tokyo thế nào?"}]

# --- Lần gọi 1: LLM quyết định ---
resp = client.chat.completions.create(model="gpt-4o", messages=messages, tools=tools)
msg = resp.choices[0].message

if msg.tool_calls:                              # LLM muốn gọi tool
    messages.append(msg)                        # lưu lại "ý định gọi tool" của LLM
    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments)        # parse tham số JSON
        result = dispatch[tc.function.name](**args)     # CHẠY hàm thật
        messages.append({                               # trả kết quả về cho LLM
            "role": "tool",
            "tool_call_id": tc.id,
            "content": str(result),
        })
    # --- Lần gọi 2: LLM dùng kết quả tool để trả lời cuối ---
    resp = client.chat.completions.create(model="gpt-4o", messages=messages, tools=tools)
    msg = resp.choices[0].message

print(msg.content)   # "Tokyo hiện 15°C, có mưa nhẹ."
```

**Với Anthropic (Claude)** ý tưởng giống hệt, chỉ khác tên field: tool trả về `content` có block `type: "tool_use"`, bạn trả lại block `type: "tool_result"`. Cùng một cơ chế 4 bước.

---

## 4. THE AGENTIC LOOP — đây chính là Agent

Ở mục 3, ta gọi LLM đúng **2 lần** (cố định) → đó vẫn là **workflow**.

Nhưng nếu một tool trả kết quả khiến LLM cần gọi **tool tiếp theo**, rồi tiếp nữa... ta không biết trước bao nhiêu vòng. Bọc bước 2-3-4 trong một **vòng `while`** cho tới khi LLM không gọi tool nữa → **bạn vừa tạo ra một Agent**:

```
        ┌─────────────────────────────┐
        │  Gọi LLM (kèm tools)        │ ◀──────────┐
        └──────────────┬──────────────┘            │
                       ▼                            │
            LLM có gọi tool không?                  │
              │ Có                  │ Không          │
              ▼                     ▼                │
   ┌──────────────────┐    ┌──────────────┐         │
   │ Chạy tool, append│    │ Trả lời cuối │ ──▶ XONG │
   │ kết quả vào msg  │────┴──────────────┘         │
   └──────────────────┘                             │
              └──────────────────────────────────────┘
                 (lặp — số vòng do LLM tự quyết)
```

```python
def agent(user_input, tools, dispatch, max_steps=10):
    messages = [{"role": "user", "content": user_input}]
    for _ in range(max_steps):                      # max_steps: phanh an toàn
        resp = client.chat.completions.create(model="gpt-4o", messages=messages, tools=tools)
        msg = resp.choices[0].message
        if not msg.tool_calls:                       # LLM không cần tool nữa -> xong
            return msg.content
        messages.append(msg)
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = dispatch[tc.function.name](**args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})
    return "Đã đạt giới hạn số bước."
```

> 💡 So sánh với buổi trước: vòng `while` này **giống hệt** cấu trúc Evaluator–Optimizer (Bài 6) — chỉ khác "điều kiện dừng" giờ là *"LLM không gọi tool nữa"* thay vì *"evaluator nói ĐẠT"*. Bạn đã quen pattern này rồi.

---

## 5. Những điều phải nhớ (an toàn & thực chiến)

1. **Luôn có `max_steps`** — phanh chống vòng lặp vô tận (tốn tiền/treo).
2. **Tool có thể lỗi** — bọc `try/except`, trả thông báo lỗi *về cho LLM* (dạng string) để nó tự xử lý/thử lại, đừng để crash.
3. **Validate tham số** — LLM có thể sinh args sai kiểu; kiểm tra trước khi chạy hàm nguy hiểm.
4. **Tool nguy hiểm cần xác nhận** — xóa file, gửi tiền, chạy lệnh shell → nên hỏi người dùng trước khi thực thi.
5. **Mô tả tool tốt = nửa thành công** — đây là "prompt engineering" cho tool.

---

## 6. Tự kiểm tra hiểu bài

1. LLM có tự chạy hàm Python của bạn không? Ai chạy?
2. Tại sao mục 3 (gọi 2 lần) là workflow, còn mục 4 (while loop) là agent?
3. Field nào trong tool schema quyết định LLM có chọn đúng tool hay không?
4. Khi tool báo lỗi, nên làm gì — crash hay trả lỗi về LLM? Vì sao?
5. `max_steps` để làm gì?

> Làm xong → mở `02-bai-tap-tool-use.md`. Hết bài tập đó là bạn đã **chạm tay vào Agent đầu tiên**.
