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
        model="gpt-5-mini",
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
        system_prompt="Trước mỗi hành động, ghi 'Suy nghĩ: ...' giải thích vì sao chọn tool.",
        max_steps=5
    )

    user_input = "Tổng dân số của Việt Nam và Nhật Bản là bao nhiêu?"
    ret = agent.run(user_input)
    print(f"> agent: {ret}")

#output:

# PS D:\workspace\ai_study\ai-agent> python .\practise\A5.py

# Suy nghĩ: Gọi tra cứu thông tin của hai quốc gia cùng lúc bằng multi_tool_use.parallel để lấy nhanh dân số của Việt Nam và Nhật Bản.

# Calling tool: tra_cuu with arguments: {'country': 'Việt Nam'}
# Result from tra_cuu: Thủ đô: Hà Nội, Dân số: 97 triệu
# Calling tool: tra_cuu with arguments: {'country': 'Nhật Bản'}
# Result from tra_cuu: Thủ đô: Tokyo, Dân số: 126 triệu

# Kết luận: Suy nghĩ: Tôi sẽ cộng hai con số dân số vừa tra cứu để trả lời câu hỏi một cách trực tiếp và rõ ràng.

# Dân số (theo kết quả tra cứu):
# - Việt Nam: 97 triệu
# - Nhật Bản: 126 triệu

# Tổng dân số = 97.000.000 + 126.000.000 = 223.000.000 (khoảng 223 triệu người).

# Ghi chú: Các số trên là làm tròn theo kết quả tra cứu; con số thực tế có thể thay đổi theo nguồn và thời điểm.
# > agent: Suy nghĩ: Tôi sẽ cộng hai con số dân số vừa tra cứu để trả lời câu hỏi một cách trực tiếp và rõ ràng.

# Dân số (theo kết quả tra cứu):
# - Việt Nam: 97 triệu
# - Nhật Bản: 126 triệu

# Tổng dân số = 97.000.000 + 126.000.000 = 223.000.000 (khoảng 223 triệu người).

# Ghi chú: Các số trên là làm tròn theo kết quả tra cứu; con số thực tế có thể thay đổi theo nguồn và thời điểm.