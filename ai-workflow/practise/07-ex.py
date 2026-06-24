import sys
from pathlib import Path
import concurrent.futures

sys.path.append(str(Path(__file__).parent.parent))
from llm import llm

# ----- Bước 1: ROUTING - phân loại phản hồi -----
def customer_feedback_classify(feedback):
    prompt = f"Phân loại phản hồi khách hàng sau, chỉ trả về duy nhất một từ: 'COMPLAINT', 'QUESTION' hoặc 'SUGGESTION':\n{feedback}"
    return llm(prompt, model="cheap", provider="openai")


# ----- Bước 2: với COMPLAINT -> PARALLELIZATION (đánh giá mức độ + soạn phản hồi) -----
def evaluate_complaint_severity_level(feedback):
    prompt = f"Đánh giá mức độ nghiêm trọng của khiếu nại sau, chỉ trả về duy nhất 'Cao', 'Trung bình' hoặc 'Thấp':\n{feedback}"
    return llm(prompt, model="cheap", provider="openai")


def generate_response_to_complaint(feedback, improvement=None):
    prompt = f"Viết một phản hồi lịch sự, chuyên nghiệp để xoa dịu khách hàng cho khiếu nại sau:\n{feedback}"
    if improvement:
        # 🔑 đưa góp ý của evaluator vào để cải thiện ở vòng sau
        prompt += f"\n\nPhản hồi trước chưa đạt, hãy sửa theo góp ý:\n{improvement}"
    return llm(prompt, model="cheap", provider="openai")


def complaint_handler(feedback):
    # chạy song song: đánh giá mức độ + soạn phản hồi ban đầu
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_severity = executor.submit(evaluate_complaint_severity_level, feedback)
        future_response = executor.submit(generate_response_to_complaint, feedback)

        severity = future_severity.result()
        response = future_response.result()

    print(f"Mức độ nghiêm trọng: {severity}")
    print(f"Phản hồi ban đầu: {response}")
    return severity, response


# ----- Bước 3: EVALUATOR-OPTIMIZER - chấm và cải thiện phản hồi -----
def evaluate_response_quality(original_feedback, generated_response):
    prompt = (
        "Dựa vào tiêu chí: lịch sự, chuyên nghiệp, giải quyết vấn đề và xoa dịu được khách hàng, "
        "hãy đánh giá phản hồi dưới đây. Nếu đạt, trả về đúng chữ 'ĐẠT'. "
        "Nếu chưa đạt, nêu góp ý cụ thể để cải thiện (không cần ghi 'ĐẠT').\n\n"
        f"Khiếu nại gốc: {original_feedback}\n"
        f"Phản hồi cần chấm: {generated_response}"
    )
    return llm(prompt, model="cheap", provider="openai")


def pipeline(feedback):
    classification = customer_feedback_classify(feedback).upper()
    print(f"Phân loại phản hồi: {classification}")

    if "COMPLAINT" in classification:
        severity, response = complaint_handler(feedback)

        # vòng lặp evaluator-optimizer: chấm -> nếu chưa đạt thì TẠO LẠI dựa trên góp ý
        for i in range(5):
            evaluation = evaluate_response_quality(feedback, response)
            if "ĐẠT" in evaluation.strip().upper():
                print(f"\n[Vòng {i+1}] Phản hồi ĐẠT chất lượng.")
                print(f"Phản hồi cuối:\n{response}")
                return
            # 🔑 chưa đạt -> dùng góp ý để sinh lại phản hồi mới
            print(f"\n[Vòng {i+1}] Chưa đạt. Góp ý: {evaluation}")
            response = generate_response_to_complaint(feedback, improvement=evaluation)
            print(f"[Vòng {i+1}] Phản hồi mới: {response}")

        print("\nChưa đạt chất lượng sau 5 vòng. Phản hồi tốt nhất hiện có:")
        print(response)

    elif "QUESTION" in classification:
        print("Đây là câu hỏi (Q&A). Không cần xử lý thêm trong demo này.")
    elif "SUGGESTION" in classification:
        print("Đây là góp ý. Không cần xử lý thêm trong demo này.")
    else:
        print(f"Không nhận diện được loại phản hồi: {classification}")


if __name__ == "__main__":
    feedback = "Tôi đã mua sản phẩm của bạn và nó bị hỏng ngay sau khi mở hộp. Tôi rất thất vọng và muốn được hoàn tiền hoặc đổi sản phẩm mới."
    pipeline(feedback)
