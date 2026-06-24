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
    },
    {
        "type": "function",
        "function": {
            "name": "tra_cuu",
            "description": "Tra cứu thông tin về một quốc gia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string", "description": "Tên quốc gia cần tra cứu"}
                },
                "required": ["country"]
            }
        }
    }
]

def cong_hai_so(a, b):
    return a + b

def tra_cuu(country):
    # This is a mock implementation - replace with actual country lookup
    country_info = {
        "Việt Nam": "Thủ đô: Hà Nội, Dân số: 97 triệu",
        "Nhật Bản": "Thủ đô: Tokyo, Dân số: 126 triệu"
    }
    return country_info.get(country, "Không tìm thấy thông tin về quốc gia này.")
dispatch = {
    "cong_hai_so": cong_hai_so,
    "tra_cuu": tra_cuu
}

def agent(user_input, max_steps=10):
    messages = [
        {"role": "user", "content": user_input}
    ]
    while max_steps > 0:
        max_steps -= 1
        
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append(msg)  # 🔑 lưu lại message assistant chứa tool_calls TRƯỚC khi thêm kết quả tool
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"Đang gọi công cụ: {tool_name} với các tham số: {tool_args}")
                if tool_name in dispatch:
                    try:
                        result = dispatch[tool_name](**tool_args)
                        print(f"Kết quả của {tool_name}: {result}")
                        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})
                    except Exception as e:
                        print(f"Lỗi khi gọi công cụ {tool_name}: {e}")
                        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(e)})
                else:
                    print(f"Công cụ {tool_name} không được định nghĩa.")
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": f"Công cụ {tool_name} không được định nghĩa."})
        else:
            print(f"Phản hồi từ mô hình: {msg.content}")
            break  # Exit the loop if no tool calls are made


if __name__ == "__main__":
    user_input = "Tổng dân số của Việt Nam và Nhật Bản là bao nhiêu?"
    agent(user_input)

# #output:
# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/T5.py 
# Đang gọi công cụ: tra_cuu với các tham số: {'country': 'Việt Nam'}
# Kết quả của tra_cuu: Thủ đô: Hà Nội, Dân số: 97 triệu
# Đang gọi công cụ: tra_cuu với các tham số: {'country': 'Nhật Bản'}
# Kết quả của tra_cuu: Thủ đô: Tokyo, Dân số: 126 triệu
# Đang gọi công cụ: cong_hai_so với các tham số: {'a': 97, 'b': 126}
# Kết quả của cong_hai_so: 223
# Phản hồi từ mô hình: Tổng dân số của Việt Nam và Nhật Bản là 223 triệu người.