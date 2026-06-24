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
    } 
]

def get_weather(city):
    # This is a mock implementation - replace with actual weather API call
    return f"Thời tiết tại {city} là 25 độ C."

dispatch = {
    "get_weather": get_weather
}

# messages = [
#     {"role": "user", "content": "Tokyo nóng không?"}
# ]
messages = [
    {"role": "user", "content": "Cho mình xem thời tiết Đà Nẵng?"}
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

#output:
# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/T1.py 
# Đang gọi công cụ: get_weather với các tham số: {'city': 'Tokyo'}
# Kết quả của get_weather: Thời tiết tại Tokyo là 25 độ C.
# Phản hồi cuối cùng từ mô hình: Hiện tại, thời tiết ở Tokyo là 25 độ C. Nhiệt độ này khá ôn hòa, không quá nóng.
# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/T1.py 
# Đang gọi công cụ: get_weather với các tham số: {'city': 'Đà Nẵng'}
# Kết quả của get_weather: Thời tiết tại Đà Nẵng là 25 độ C.
# Phản hồi cuối cùng từ mô hình: Thời tiết tại Đà Nẵng hiện tại là 25 độ C.