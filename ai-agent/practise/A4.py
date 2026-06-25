import json
from agent import Agent




if __name__ == "__main__":

    def cong_hai_so(a, b):
        return a + b

    def tra_cuu(country):
        # This is a mock implementation - replace with actual country lookup
        country_info = {
            "Việt Nam": "Thủ đô: Hà Nội, Dân số: 97 triệu",
            "Nhật Bản": "Thủ đô: Tokyo, Dân số: 126 triệu"
        }
        return country_info.get(country, "Không tìm thấy thông tin về quốc gia này.")

    def doi_tien(amount, from_cur, to_cur):
        mock_exchange_rate = 0.85  # Mock exchange rate for demonstration
        converted_amount = amount * mock_exchange_rate
        return converted_amount

    def gui_tien(amount, to_account):
        print(f"Sent {amount}USD to account: {to_account}")

    dispatch = {
        "cong_hai_so": cong_hai_so,
        "tra_cuu": tra_cuu,
        "doi_tien": doi_tien,
        "gui_tien": gui_tien
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
                    },
                    "request_accept": False
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
                    },
                    "request_accept": False
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "gui_tien",
                    "description": "Gửi tiền tới một tài khoản khác.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number", "description": "Số tiền cần gửi"},
                            "to_account": {"type": "string", "description": "Số tài khoản nhận tiền"}
                        },
                        "required": ["amount", "to_account"]
                    },
                    "request_accept": True
                }
            }    
        ],
        dispatch=dispatch,
        system_prompt="Bạn là một trợ lý hữu ích, có khả năng tra cứu thông tin về các quốc gia và thực hiện các phép tính cơ bản.",
        max_steps=5
    )

    user_input = "Tôi cần gửi 100USD tới số tài khoản 12345678"
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