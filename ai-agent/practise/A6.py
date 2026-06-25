import json
from agent import Agent


def nghien_cuu(query):
    def tra_cuu(country):
        # This is a mock implementation - replace with actual country lookup
        country_info = {
            "Việt Nam": "Thủ đô: Hà Nội, Dân số: 97 triệu",
            "Nhật Bản": "Thủ đô: Tokyo, Dân số: 126 triệu"
        }
        return country_info.get(country, "Không tìm thấy thông tin về quốc gia này.")
    
    dispatch = {
        "tra_cuu": tra_cuu
    }

    agent = Agent(
        model="gpt-4o",
        tools=[
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
                    },
                    "request_accept": False
                }
            }
        ],
        dispatch=dispatch,
        system_prompt="Bạn là một trợ lý hữu ích, có khả năng tra cứu thông tin về các quốc gia.",
        max_steps=5
    )

    def run_query(query):
        return agent.run(query)
    
    result = run_query(query)
    return result


def tinh_toan(query):
    def cong_hai_so(a, b):
        return a + b

    dispatch = {
        "cong_hai_so": cong_hai_so
    }

    agent = Agent(
        model="gpt-4o",
        tools=[
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
                    },
                    "request_accept": False
                }
            }
        ],
        dispatch=dispatch,
        system_prompt="Bạn là một trợ lý hữu ích, có khả năng thực hiện các phép tính cơ bản.",
        max_steps=5
    )

    def run_query(query):
        return agent.run(query)
    
    result = run_query(query)
    return result


if __name__ == "__main__":


    dispatch = {
        "nghien_cuu": nghien_cuu,
        "tinh_toan": tinh_toan
    }

    agent = Agent(
        model="gpt-4o",
        tools=[
            {
                "type": "function", 
                "function": {
                    "name": "nghien_cuu",
                    "description": "Nghiên cứu thông tin về một quốc gia.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Câu hỏi nghiên cứu về quốc gia"},
                        },
                        "required": ["query"]
                    },
                    "request_accept": False
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tinh_toan",
                    "description": "Thực hiện các phép tính dựa trên câu hỏi của người dùng.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Câu hỏi về phép tính"},
                        },
                        "required": ["query"]
                    },
                    "request_accept": False
                }
            }
        ],
        dispatch=dispatch,
        system_prompt="Bạn là một trợ lý hữu ích, có khả năng tra cứu thông tin về các quốc gia và thực hiện các phép tính cơ bản.",
        max_steps=5
    )

    user_input = "Tổng dân số của Việt Nam và Nhật Bản là bao nhiêu?"
    ret = agent.run(user_input)
    print(f"> agent: {ret}")

#output:

# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/A4.py 
# Cho phép chạy gui_tien({'amount': 100, 'to_account': '12345678'})? [y/N] N 
# Model response: Tôi không thể thực hiện việc gửi tiền cho bạn. Nếu bạn cần hỗ trợ hoặc có câu hỏi khác, hãy cho tôi biết nhé!
# > agent: Tôi không thể thực hiện việc gửi tiền cho bạn. Nếu bạn cần hỗ trợ hoặc có câu hỏi khác, hãy cho tôi biết nhé!
# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/A4.py 
# Cho phép chạy gui_tien({'amount': 100, 'to_account': '12345678'})? [y/N] y
# User accepted calling tool: gui_tien
# Calling tool: gui_tien with arguments: {'amount': 100, 'to_account': '12345678'}
# Sent 100USD to account: 12345678
# Result from gui_tien: None
# Model response: Tôi đã gửi 100 USD tới số tài khoản 12345678 thành công.
# > agent: Tôi đã gửi 100 USD tới số tài khoản 12345678 thành công.
# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ 