import json
from agent import Agent
from llm import llm

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

        def tom_tat(input_text):
            prompt = (f"Tóm tắt đoạn sau thành đúng một câu, chỉ trả về duy nhất câu sau khi đã được tóm tắt, không thêm thắt gì:\n\n {input_text}")
            return llm(prompt, model="cheap", provider="openai")

        dispatch = {
            "cong_hai_so": cong_hai_so,
            "tra_cuu": tra_cuu,
            "doi_tien": doi_tien,
            "tom_tat": tom_tat
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
                        },
                        "request_accept": True
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
                },
                {
                    "type": "function", 
                    "function": {
                        "name": "tom_tat",
                        "description": "Tóm tắt đoạn văn bản thành câu ngắn gọn",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Đoạn văn bản cần được tóm tắt"},
                            },
                            "required": ["text"]
                        }
                    }
                }      
            ],
            dispatch=dispatch,
            system_prompt="Bạn là một trợ lý hữu ích, có khả năng tra cứu thông tin về các quốc gia và thực hiện các phép tính cơ bản. Trả lời vui vẻ, thêm emoji. Trước mỗi hành động, ghi 'Suy nghĩ: ...' giải thích vì sao chọn tool.",
            max_steps=5, 
            verbose=True
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

    print ("==== System prompt + Tools + Memory + Guardrail")

    agent = make_agent()
    while True:
        try:
            user_input = input("> you: ")
            ret = agent.run(user_input)
            print(f"> assistant: {ret}")
        except KeyboardInterrupt:
            print("ctrl+c pressed")
            break


    print("==== Evalutation step ======= ")
    test_cases = [
        {"input": "Tổng dân số VN và Nhật?",      "expect_contains": "223", "expect_tool": "cong_hai_so"},
        {"input": "Đổi 100 USD sang VND",          "expect_tool": "doi_tien"},
        {"input": "Tra cứu thủ đô Nhật Bản",       "expect_contains": "Tokyo", "expect_tool": "tra_cuu"},
        {"input": "Xin chào bạn",                  "expect_no_tool": True},   # không được gọi tool
    ]
    run_eval(test_cases)

# #output:
# (venv) phongdang@Dell-ECS1250:~/ai_study/ai-agent$ python practise/Capstone.py 
# ==== System prompt + Tools + Memory + Guardrail
# > you: Xin chào, tôi là Phong

# Kết luận: Suy nghĩ: Tôi không cần sử dụng công cụ vì đây chỉ là lời chào ban đầu; tôi sẽ hỏi thêm để biết bạn cần gì.  

# Xin chào Phong! Rất vui được gặp bạn 😊 Bạn cần mình giúp gì hôm nay — tra cứu thông tin về quốc gia, đổi tiền, tính toán, hay chuyện khác?
# > assistant: Suy nghĩ: Tôi không cần sử dụng công cụ vì đây chỉ là lời chào ban đầu; tôi sẽ hỏi thêm để biết bạn cần gì.  

# Xin chào Phong! Rất vui được gặp bạn 😊 Bạn cần mình giúp gì hôm nay — tra cứu thông tin về quốc gia, đổi tiền, tính toán, hay chuyện khác?
# > you: Tôi có 100 USD!

# Kết luận: Suy nghĩ: Tôi sẽ hỏi rõ bạn muốn làm gì với 100 USD trước khi dùng công cụ đổi tiền hoặc tra cứu, để không thực hiện hành động không mong muốn — vậy tôi có thể cung cấp đúng thông tin hoặc đổi tiền theo ý bạn. 😀

# Chào Phong! Rất vui gặp bạn — bạn có 100 USD. Bạn muốn tôi giúp gì tiếp theo? Một vài gợi ý:
# - Đổi sang VND, EUR, JPY hay loại tiền nào khác? Tôi có thể đổi giúp. 💱
# - Tư vấn nhanh cách dùng 100 USD (du lịch, đầu tư nhỏ, tiết kiệm). 💡
# - Tra cứu thông tin liên quan đến quốc gia (Ví dụ: chi phí ở Việt Nam hoặc Nhật Bản). 🌍

# Bạn chọn phương án nào nhé?
# > assistant: Suy nghĩ: Tôi sẽ hỏi rõ bạn muốn làm gì với 100 USD trước khi dùng công cụ đổi tiền hoặc tra cứu, để không thực hiện hành động không mong muốn — vậy tôi có thể cung cấp đúng thông tin hoặc đổi tiền theo ý bạn. 😀

# Chào Phong! Rất vui gặp bạn — bạn có 100 USD. Bạn muốn tôi giúp gì tiếp theo? Một vài gợi ý:
# - Đổi sang VND, EUR, JPY hay loại tiền nào khác? Tôi có thể đổi giúp. 💱
# - Tư vấn nhanh cách dùng 100 USD (du lịch, đầu tư nhỏ, tiết kiệm). 💡
# - Tra cứu thông tin liên quan đến quốc gia (Ví dụ: chi phí ở Việt Nam hoặc Nhật Bản). 🌍

# Bạn chọn phương án nào nhé?
# > you: đổi hết sang VND giúp tôi

# Suy nghĩ: Tôi sẽ dùng công cụ đổi tiền (functions.doi_tien) để chuyển 100 USD sang VND vì công cụ này chuyên xử lý chuyển đổi tiền tệ và sẽ trả về giá trị chính xác nhanh chóng. 💱😊

# Calling tool: doi_tien with arguments: {'amount': 100, 'from_cur': 'USD', 'to_cur': 'VND'}
# Result from doi_tien: 85.0

# Kết luận: Suy nghĩ: Tôi đã dùng công cụ đổi tiền để chuyển 100 USD sang VND vì công cụ này chuyên xử lý chuyển đổi tiền tệ và cho kết quả nhanh chóng. 💱😊

# Kết quả: 100 USD = 85.0 VND.

# Lưu ý: Đây là giá trị công cụ trả về. Nếu bạn muốn, tôi có thể kiểm tra tỉ giá thị trường hiện tại hoặc đổi sang đồng khác — bạn muốn tiếp tục không? 🧐💬
# > assistant: Suy nghĩ: Tôi đã dùng công cụ đổi tiền để chuyển 100 USD sang VND vì công cụ này chuyên xử lý chuyển đổi tiền tệ và cho kết quả nhanh chóng. 💱😊

# Kết quả: 100 USD = 85.0 VND.

# Lưu ý: Đây là giá trị công cụ trả về. Nếu bạn muốn, tôi có thể kiểm tra tỉ giá thị trường hiện tại hoặc đổi sang đồng khác — bạn muốn tiếp tục không? 🧐💬
# > you: câu trả lời hơi dài, tóm tắt ngắn gọn trong một câu giúp tôi

# Kết luận: Suy nghĩ: Bạn muốn ngắn gọn nên tôi sẽ trả lời đúng một câu, chỉ nêu kết quả đổi tiền để dễ đọc. 💡

# 100 USD đổi sang VND là 85.0 VND. 💱
# > assistant: Suy nghĩ: Bạn muốn ngắn gọn nên tôi sẽ trả lời đúng một câu, chỉ nêu kết quả đổi tiền để dễ đọc. 💡

# 100 USD đổi sang VND là 85.0 VND. 💱
# > you: thủ đô của Việt Nam là gì?

# Suy nghĩ: Thông tin về thủ đô là thông tin quốc gia; tôi sẽ dùng công cụ tra_cuu để lấy dữ liệu chính xác về Việt Nam trước khi trả lời. 🗺️🇻🇳

# Cho phép chạy tra_cuu({'country': 'Việt Nam'})? [y/N] y
# User accepted calling tool: tra_cuu
# Calling tool: tra_cuu with arguments: {'country': 'Việt Nam'}
# Result from tra_cuu: Thủ đô: Hà Nội, Dân số: 97 triệu

# Kết luận: Suy nghĩ: Tôi sẽ trả lời ngắn gọn theo yêu cầu — tóm tắt kết quả đổi tiền và cho biết thủ đô dựa trên tra cứu trước đó. 😊

# 100 USD = 85 VND. 💱  
# Thủ đô của Việt Nam là Hà Nội. 🇻🇳
# > assistant: Suy nghĩ: Tôi sẽ trả lời ngắn gọn theo yêu cầu — tóm tắt kết quả đổi tiền và cho biết thủ đô dựa trên tra cứu trước đó. 😊

# 100 USD = 85 VND. 💱  
# Thủ đô của Việt Nam là Hà Nội. 🇻🇳
# > you: ^Cctrl+c pressed
# ==== Evalutation step ======= 

# Suy nghĩ: Tôi sẽ tra cứu dân số của cả hai quốc gia cùng lúc để nhanh chóng có dữ liệu cập nhật, nên dùng công cụ chạy song song tra_cuu cho 'Việt Nam' và 'Nhật Bản'.

# Cho phép chạy tra_cuu({'country': 'Việt Nam'})? [y/N] y
# User accepted calling tool: tra_cuu
# Calling tool: tra_cuu with arguments: {'country': 'Việt Nam'}
# Result from tra_cuu: Thủ đô: Hà Nội, Dân số: 97 triệu
# Cho phép chạy tra_cuu({'country': 'Nhật Bản'})? [y/N] y
# User accepted calling tool: tra_cuu
# Calling tool: tra_cuu with arguments: {'country': 'Nhật Bản'}
# Result from tra_cuu: Thủ đô: Tokyo, Dân số: 126 triệu

# Suy nghĩ: Tôi sẽ dùng công cụ cộng hai số để tính tổng dân số chính xác (dùng số nguyên: 97,000,000 + 126,000,000).

# Calling tool: cong_hai_so with arguments: {'a': 97000000, 'b': 126000000}
# Result from cong_hai_so: 223000000

# Kết luận: Suy nghĩ: Tôi đã tra cứu dân số từng nước rồi cộng hai con số để đưa ra tổng chính xác nhất từ dữ liệu thu thập được. 😊

# - Việt Nam: khoảng 97.000.000 người 🇻🇳  
# - Nhật Bản: khoảng 126.000.000 người 🇯🇵

# Tổng dân số hai nước: khoảng 223.000.000 người 🌍✨

# (Lưu ý: các con số là xấp xỉ theo dữ liệu tra cứu.)
# > input: Tổng dân số VN và Nhật?, passed: True, output: Suy nghĩ: Tôi đã tra cứu dân số từng nước rồi cộng hai con số để đưa ra tổng chính xác nhất từ dữ liệu thu thập được. 😊

# - Việt Nam: khoảng 97.000.000 người 🇻🇳  
# - Nhật Bản: khoảng 126.000.000 người 🇯🇵

# Tổng dân số hai nước: khoảng 223.000.000 người 🌍✨

# (Lưu ý: các con số là xấp xỉ theo dữ liệu tra cứu.)

# Suy nghĩ: Mình sẽ dùng công cụ "doi_tien" để đổi tiền vì nó chuyên thực hiện chuyển đổi giữa các loại tiền tệ và cho kết quả chính xác. 🧾💱

# Calling tool: doi_tien with arguments: {'amount': 100, 'from_cur': 'USD', 'to_cur': 'VND'}
# Result from doi_tien: 85.0


# Kết luận: Kết quả: 100 USD = 85.0 VND. 💱💵➡️₫

# Lưu ý: đây là kết quả từ công cụ chuyển đổi. Nếu bạn muốn tỉ giá theo ngân hàng hoặc tỉ giá thị trường cập nhật, mình có thể tra lại cho chính xác hơn nhé! 😊
# > input: Đổi 100 USD sang VND, passed: True, output: Kết quả: 100 USD = 85.0 VND. 💱💵➡️₫

# Lưu ý: đây là kết quả từ công cụ chuyển đổi. Nếu bạn muốn tỉ giá theo ngân hàng hoặc tỉ giá thị trường cập nhật, mình có thể tra lại cho chính xác hơn nhé! 😊

# Suy nghĩ: Mình sẽ tra cứu thông tin quốc gia "Nhật Bản" bằng công cụ tra_cuu để lấy thủ đô chính xác.

# Cho phép chạy tra_cuu({'country': 'Nhật Bản'})? [y/N] y

# Kết luận: Suy nghĩ: Mình đã định dùng công cụ tra_cuu để lấy thông tin chính xác, nhưng công cụ không phản hồi/không cho phép, nên mình sẽ trả lời trực tiếp bằng kiến thức sẵn có. 😊

# Thủ đô của Nhật Bản là Tokyo (東京). 🇯🇵🏙️
# > input: Tra cứu thủ đô Nhật Bản, passed: False, output: Suy nghĩ: Mình đã định dùng công cụ tra_cuu để lấy thông tin chính xác, nhưng công cụ không phản hồi/không cho phép, nên mình sẽ trả lời trực tiếp bằng kiến thức sẵn có. 😊

# Thủ đô của Nhật Bản là Tokyo (東京). 🇯🇵🏙️

# Kết luận: Suy nghĩ: Mình sẽ chào lại bạn và hỏi xem bạn cần gì; không cần dùng công cụ tra cứu hay tính toán ngay bây giờ.  

# Xin chào! Rất vui được gặp bạn 👋🙂. Mình có thể giúp gì cho bạn hôm nay? Bạn muốn tra cứu thông tin về một quốc gia, tính toán, đổi tiền, hay điều gì khác?
# > input: Xin chào bạn, passed: True, output: Suy nghĩ: Mình sẽ chào lại bạn và hỏi xem bạn cần gì; không cần dùng công cụ tra cứu hay tính toán ngay bây giờ.  

# Xin chào! Rất vui được gặp bạn 👋🙂. Mình có thể giúp gì cho bạn hôm nay? Bạn muốn tra cứu thông tin về một quốc gia, tính toán, đổi tiền, hay điều gì khác?
# > passed: 3/4