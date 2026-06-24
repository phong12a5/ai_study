import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from llm import llm

def classify_input(input_question):
    prompt = f"Phân loại câu hỏi sau: '{input_question}' thành 3 loại: 'giải toán', 'viết code', và 'chung'.Chỉ trả về một từ duy nhất tương ứng: 'TOAN', 'CODE 'hoặc 'CHUNG'."
    return llm(prompt, model="cheap", provider="openai")

def mapping_model(category):
    if category == "TOAN":
        return "strong"
    elif category == "CODE":
        return "strong"
    else:
        return "cheap"

if __name__ == "__main__":
    input_question = "Tính tích phân của hàm số f(x) = x^2 từ 0 đến 1."
    category = classify_input(input_question)
    model = mapping_model(category)
    print(f"Câu hỏi: {input_question}")
    print(f"Phân loại: {category}, Model được chọn: {model}")


    