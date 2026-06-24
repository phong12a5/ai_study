import json
from openai import OpenAI
client = OpenAI()
MODEL = "gpt-4o"  


tools = [
    {
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
    },
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
            "name": "doi_tien",
            "description": "Đổi tiền tệ từ một loại sang loại khác.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Số tiền cần đổi"},
                    "from_cur": {"type": "string", "description": "Mã tiền tệ gốc, ví dụ: 'USD'"},
                    "to_cur": {"type": "string", "description": "Mã tiền tệ đích, ví dụ: 'EUR'"}
                },
                "required": ["amount", "from_cur", "to_cur"]
            }
        }
    }   
]

def get_weather(city):
    # This is a mock implementation - replace with actual weather API call
    return f"Thời tiết tại {city} là 25 độ C."

def cong_hai_so(a, b):
    return a + b

def doi_tien(amount, from_cur, to_cur):
    mock_exchange_rate = 0.85  # Mock exchange rate for demonstration
    converted_amount = amount * mock_exchange_rate
    return converted_amount

dispatch = {
    "get_weather": get_weather,
    "cong_hai_so": cong_hai_so,
    "doi_tien": doi_tien
}

# messages = [
#     {"role": "user", "content": "Xin chào!"}
# ]
# messages = [
#     {"role": "user", "content": "Tokyo nóng không?"}
# ]


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
                    result = dispatch[tool_name](**tool_args)
                    print(f"Kết quả của {tool_name}: {result}")
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})
                else:
                    print(f"Công cụ {tool_name} không được định nghĩa.")
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": f"Công cụ {tool_name} không được định nghĩa."})
        else:
            print(f"Phản hồi từ mô hình: {msg.content}")
            break  # Exit the loop if no tool calls are made


if __name__ == "__main__":
    user_input = "Đổi 100 USD sang VND, rồi cộng thêm 50000 vào kết quả đó."
    agent(user_input)

#output:
#(venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/T3.py 
# Đang gọi công cụ: doi_tien với các tham số: {'amount': 100, 'from_cur': 'USD', 'to_cur': 'VND'}
# Kết quả của doi_tien: 85.0
# Đang gọi công cụ: cong_hai_so với các tham số: {'a': 85.0, 'b': 50000}
# Kết quả của cong_hai_so: 50085.0
# Phản hồi từ mô hình: Sau khi đổi 100 USD sang VND và cộng thêm 50,000, kết quả là 50,085.
