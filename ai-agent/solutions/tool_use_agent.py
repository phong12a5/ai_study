"""Bài T3 — Vòng lặp Agent đầu tiên với OpenAI function calling.
Chạy: python solutions/tool_use_agent.py
Yêu cầu: export OPENAI_API_KEY=...
"""
import json
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4o"

# ---------- Các hàm Python THẬT ----------
def get_weather(city):
    return {"Hà Nội": "28°C, nắng", "Tokyo": "15°C, mưa nhẹ"}.get(city, "Không có dữ liệu")

def cong_hai_so(a, b):
    return a + b

def doi_tien(amount, from_cur, to_cur):
    ti_gia = {("USD", "VND"): 25000, ("VND", "USD"): 1 / 25000}
    rate = ti_gia.get((from_cur, to_cur))
    if rate is None:
        raise ValueError(f"Không hỗ trợ đổi {from_cur} -> {to_cur}")
    return amount * rate

dispatch = {"get_weather": get_weather, "cong_hai_so": cong_hai_so, "doi_tien": doi_tien}

# ---------- Mô tả tool (JSON schema) ----------
tools = [
    {"type": "function", "function": {
        "name": "get_weather",
        "description": "Lấy thời tiết hiện tại của một thành phố.",
        "parameters": {"type": "object",
            "properties": {"city": {"type": "string", "description": "Tên thành phố"}},
            "required": ["city"]}}},
    {"type": "function", "function": {
        "name": "cong_hai_so",
        "description": "Cộng hai số và trả về tổng.",
        "parameters": {"type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"]}}},
    {"type": "function", "function": {
        "name": "doi_tien",
        "description": "Đổi tiền giữa hai loại tiền tệ, ví dụ USD sang VND.",
        "parameters": {"type": "object",
            "properties": {"amount": {"type": "number"},
                           "from_cur": {"type": "string", "description": "Mã tiền nguồn, vd USD"},
                           "to_cur": {"type": "string", "description": "Mã tiền đích, vd VND"}},
            "required": ["amount", "from_cur", "to_cur"]}}},
]

# ---------- Vòng lặp Agent ----------
def agent(user_input, max_steps=10):
    messages = [{"role": "user", "content": user_input}]
    for step in range(1, max_steps + 1):
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        msg = resp.choices[0].message

        if not msg.tool_calls:                 # LLM không cần tool nữa -> xong
            return msg.content

        messages.append(msg)                   # lưu "ý định gọi tool"
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"[Bước {step}] LLM gọi: {tc.function.name}({args})")
            try:
                result = dispatch[tc.function.name](**args)   # T4: bọc try/except
            except Exception as e:
                result = f"LỖI: {e}"           # trả lỗi VỀ cho LLM tự xử lý
            print(f"          -> kết quả: {result}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})
    return "Đã đạt giới hạn số bước."


if __name__ == "__main__":
    cau = "Đổi 100 USD sang VND, rồi cộng thêm 50000 vào kết quả đó."
    print("Câu hỏi:", cau, "\n")
    print("\nTRẢ LỜI CUỐI:", agent(cau))
