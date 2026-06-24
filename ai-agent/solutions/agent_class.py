"""Bài A1 — Lớp Agent tái sử dụng (nền cho cả module Agent chuyên sâu).
Đã sửa 3 lỗi tiềm ẩn từ T2-T5:
  1. Mọi tool_call đều trả về một tool message (kể cả tool lạ / lỗi) -> không còn lỗi 400.
  2. except Exception (không chỉ ValueError) -> tool không bao giờ làm sập vòng lặp.
  3. run() trả về kết quả; hết max_steps trả fallback.
Chạy: python solutions/agent_class.py
"""
import json
from openai import OpenAI


class Agent:
    def __init__(self, tools, dispatch, system="", model="gpt-4o", max_steps=10,
                 dangerous=None, verbose=True):
        self.client = OpenAI()
        self.tools = tools
        self.dispatch = dispatch
        self.model = model
        self.max_steps = max_steps
        self.dangerous = set(dangerous or [])      # tool cần xác nhận (A4)
        self.verbose = verbose
        self.messages = []
        if system:
            self.messages.append({"role": "system", "content": system})
        self.tool_log = []                          # phục vụ eval trajectory (A7)

    def _run_tool(self, tool_call):
        """KHÔNG BAO GIỜ raise — luôn trả string (kết quả hoặc thông báo lỗi)."""
        name = tool_call.function.name
        self.tool_log.append(name)
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            return f"LỖI: tham số JSON không hợp lệ ({e})"

        fn = self.dispatch.get(name)
        if fn is None:                              # fix #1: tool lạ vẫn có message trả về
            return f"LỖI: tool '{name}' không tồn tại."

        if name in self.dangerous:                  # A4: human-in-the-loop
            if input(f"  ⚠️  Cho phép chạy {name}({args})? [y/N] ").strip().lower() != "y":
                return "Người dùng từ chối thực hiện thao tác này."

        try:
            return str(fn(**args))                   # fix #2: bắt mọi Exception
        except Exception as e:
            return f"LỖI khi chạy {name}: {e}"

    def run(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        for _ in range(self.max_steps):
            resp = self.client.chat.completions.create(
                model=self.model, messages=self.messages, tools=self.tools)
            msg = resp.choices[0].message

            if not msg.tool_calls:                   # fix #3: trả về kết quả cuối
                self.messages.append(msg)
                return msg.content

            self.messages.append(msg)                # luôn append assistant trước tool results
            for tc in msg.tool_calls:
                result = self._run_tool(tc)
                if self.verbose:
                    print(f"  [tool] {tc.function.name}({tc.function.arguments}) -> {result}")
                self.messages.append({
                    "role": "tool", "tool_call_id": tc.id, "content": result,
                })
        return "Đã đạt giới hạn số bước (max_steps)."


# ---------------- Demo ----------------
if __name__ == "__main__":
    def cong_hai_so(a, b):
        return a + b

    def tra_cuu(country):
        return {"Việt Nam": "Dân số: 97 triệu",
                "Nhật Bản": "Dân số: 126 triệu"}.get(country, "Không tìm thấy.")

    tools = [
        {"type": "function", "function": {
            "name": "cong_hai_so", "description": "Cộng hai số.",
            "parameters": {"type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"]}}},
        {"type": "function", "function": {
            "name": "tra_cuu", "description": "Tra cứu thông tin một quốc gia.",
            "parameters": {"type": "object",
                "properties": {"country": {"type": "string"}}, "required": ["country"]}}},
    ]
    dispatch = {"cong_hai_so": cong_hai_so, "tra_cuu": tra_cuu}

    agent = Agent(
        tools=tools, dispatch=dispatch,
        system="Bạn là trợ lý nghiên cứu. LUÔN dùng tool để tra cứu và tính toán, "
               "không tự bịa số. Trả lời bằng tiếng Việt.",
    )
    print("KẾT QUẢ:", agent.run("Tổng dân số của Việt Nam và Nhật Bản là bao nhiêu triệu?"))
    print("Tool đã gọi (trajectory):", agent.tool_log)
