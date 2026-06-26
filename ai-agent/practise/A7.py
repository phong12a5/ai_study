import json
from agent import Agent


if __name__ == "__main__":

    def make_agent():
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
                        "description": "Tra cứu thông tin về một quốc gia. Hỗ trợ: 'Việt Nam', 'Nhật Bản'",
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

        return agent

    def run_one(case):
        agent = make_agent()
        output = agent.run(case["input"])

        checks = []
        if "expect_contains" in case:
            checks.append(case["expect_contains"].lower() in output.lower())   # tầng 1
        if "expect_tool" in case:
            checks.append(case["expect_tool"] in agent.tool_log)               # tầng 2
        if case.get("expect_no_tool"):
            checks.append(len(agent.tool_log) == 0)

        passed = all(checks)
        return passed, output, agent.tool_log

    def run_eval(test_cases):
        pass_count = 0
        for case in test_cases:
            passed, output, tool_log = run_one(case)
            print(f"> input: {case['input']}, passed: {passed}, output: {output}")
            if passed:
                pass_count += 1
        
        print(f"> passed: {pass_count}/{len(test_cases)}")

    test_cases = [
        {"input": "Tổng dân số VN và Nhật?",      "expect_contains": "223", "expect_tool": "cong_hai_so"},
        {"input": "Đổi 100 USD sang VND",          "expect_tool": "doi_tien"},
        {"input": "Tra cứu thủ đô Nhật Bản",       "expect_contains": "Tokyo", "expect_tool": "tra_cuu"},
        {"input": "Xin chào bạn",                  "expect_no_tool": True},   # không được gọi tool
    ]
    run_eval(test_cases)

# #output:
# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/A7.py 
# > input: Tổng dân số VN và Nhật?, passed: True, output: Tổng dân số của Việt Nam và Nhật Bản là 223 triệu người.
# > input: Đổi 100 USD sang VND, passed: True, output: Hiện tại, tỷ giá ngoại tệ không khả dụng, do đó không thể đổi 100 USD sang VND. 
# > input: Tra cứu thủ đô Nhật Bản, passed: True, output: Thủ đô của Nhật Bản là Tokyo.
# > input: Xin chào bạn, passed: True, output: Xin chào! Tôi có thể giúp gì cho bạn hôm nay?
# > passed: 4/4