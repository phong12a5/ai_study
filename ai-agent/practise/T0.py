import json
from openai import OpenAI
client = OpenAI()
MODEL = "gpt-4o"  


tools = [
    {
        "type": "function", 
        "function": {
            "name": "cong_hai_so",
            "description": "Cộng hai số lại với nhau.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Số thứ nhất"},
                    "b": {"type": "number", "description": "Số thứ hai"}
                },
                "required": ["a", "b"]
            }
        }
    }   
]

def cong_hai_so(a, b):
    return a + b

dispatch = {
    "cong_hai_so": cong_hai_so
}

messages = [
    {"role": "user", "content": "Hãy cộng hai số 5 và 7."}
]

resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
msg = resp.choices[0].message

if msg.tool_calls:
    messages.append(msg)  # 🔑 lưu lại message assistant chứa tool_calls TRƯỚC khi thêm kết quả tool
    for tool_call in msg.tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        print(f"Đang gọi công cụ: {tool_name} với các tham số: {tool_args}")
        if tool_name in dispatch:
            result = dispatch[tool_name](**tool_args)
            print(f"Kết quả của {tool_name}: {result}")
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})
        else:
            print(f"Công cụ {tool_name} không được định nghĩa.")

    resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    msg = resp.choices[0].message
    print(f"Phản hồi cuối cùng từ mô hình: {msg.content}")