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

    while True:
        user_input = input("> you: ")
        ret = agent.run(user_input)
        print(f"> assistant: {ret}")

#output:

# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/A3.py 
# > you: Tên tôi là Phong, tôi có 100 USD.
# Model response: Chào Phong! Bạn muốn sử dụng số tiền 100 USD này để làm gì? Nếu bạn cần đổi tiền sang một loại tiền khác hoặc có câu hỏi gì khác, hãy cho tôi biết nhé!
# > assistant: Chào Phong! Bạn muốn sử dụng số tiền 100 USD này để làm gì? Nếu bạn cần đổi tiền sang một loại tiền khác hoặc có câu hỏi gì khác, hãy cho tôi biết nhé!
# > you: Đổi hết sang VND giúp tôi.
# Calling tool: doi_tien with arguments: {'amount': 100, 'from_cur': 'USD', 'to_cur': 'VND'}
# Result from doi_tien: 85.0
# Model response: Số tiền 100 USD của bạn sau khi đổi sẽ là 85,000 VND.
# > assistant: Số tiền 100 USD của bạn sau khi đổi sẽ là 85,000 VND.
# > you: Tôi tên gì? 
# Model response: Bạn đã cho tôi biết tên bạn là Phong.
# > assistant: Bạn đã cho tôi biết tên bạn là Phong.