import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from llm import llm

def get_three_bullet_points(product_description):
    prompt = f"Tạo ra đúng 3 ý chính để marketing sản phẩm: '{product_description}'. Mỗi ý chính là một dòng. Trả về đúng 3 dòng cho 3 ý chính."
    return llm(prompt, model="cheap", provider="openai")

def gate(bullet_points):
    lines = bullet_points.strip().split("\n")
    if len(lines) != 3:
        return False, "Kết quả không có đúng 3 dòng."
    return True, "Kết quả hợp lệ."

def generate_marketing_emails(bullet_points):
    prompt = f"Tạo ra email marketing dựa trên 3 ý chính sau:\n{bullet_points}\n, email không quá 200 từ."
    return llm(prompt, model="cheap", provider="openai")

if __name__ == "__main__":
    product_description = "Một chiếc máy pha cà phê tự động với thiết kế hiện đại, dễ sử dụng và tiết kiệm thời gian."
    for i in range(2):
        bullet_points = get_three_bullet_points(product_description)
        is_valid, message = gate(bullet_points)
        if not is_valid:
            print(f"Lần {i+1}: Kết quả không hợp lệ: {message}")
            continue
        print(f"Lần {i+1}: 3 ý chính:\n{bullet_points}\n")
        email = generate_marketing_emails(bullet_points)
        print(f"Lần {i+1}: Email marketing:\n{email}\n")
        break


    