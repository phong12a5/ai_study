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

    dispatch = {
        "cong_hai_so": cong_hai_so,
        "tra_cuu": tra_cuu,
        "doi_tien": doi_tien
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
        ],
        dispatch=dispatch,
        system_prompt="Bạn là một trợ lý hữu ích, có khả năng tra cứu thông tin về các quốc gia và thực hiện các phép tính cơ bản.",
        max_steps=5
    )

    user_input = "Tổng dân số của Việt Nam và Nhật Bản là bao nhiêu?"
    # user_input = "Đổi 100 USD sang VND, rồi cộng thêm 50000 vào kết quả đó."
    ret = agent.run(user_input)
    print(f"Final result from agent: {ret}")

# #output:
# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/A1.py 
# Calling tool: doi_tien with arguments: {'amount': 100, 'from_cur': 'USD', 'to_cur': 'VND'}
# Result from doi_tien: 85.0
# Calling tool: cong_hai_so with arguments: {'a': 85, 'b': 50000}
# Result from cong_hai_so: 50085
# Model response: Sau khi đổi 100 USD sang VND, bạn có 85 VND. Khi cộng thêm 50,000 VND vào, tổng số tiền là 50,085 VND.
# Final result from agent: Sau khi đổi 100 USD sang VND, bạn có 85 VND. Khi cộng thêm 50,000 VND vào, tổng số tiền là 50,085 VND.
# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/A1.py 
# Calling tool: tra_cuu with arguments: {'country': 'Việt Nam'}
# Result from tra_cuu: Thủ đô: Hà Nội, Dân số: 97 triệu
# Calling tool: tra_cuu with arguments: {'country': 'Nhật Bản'}
# Result from tra_cuu: Thủ đô: Tokyo, Dân số: 126 triệu
# Calling tool: cong_hai_so with arguments: {'a': 97, 'b': 126}
# Result from cong_hai_so: 223
# Model response: Tổng dân số của Việt Nam và Nhật Bản là 223 triệu người.
# Final result from agent: Tổng dân số của Việt Nam và Nhật Bản là 223 triệu người.