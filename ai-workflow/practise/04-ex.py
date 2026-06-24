import sys
from pathlib import Path
import concurrent.futures

sys.path.append(str(Path(__file__).parent.parent))
from llm import llm

def review_code(code_snippet, temperature=1.0):
    prompt = f"Kiểm trađoạn code sau có lỗ hổng bảo mật không? Trả lời: YES (lý do) hoặc NO:\n{code_snippet}"
    return llm(prompt, model="cheap", provider="openai", temperature=temperature)

def pipeline(code_snippet):
    
    check_time = 5
    max_for_warning = 3
    warning_count = 0

    for i in range(check_time):
        result = review_code(code_snippet, temperature=1.0 + i * 0.1)
        if result.strip().upper().startswith("YES"):
            warning_count += 1
            if warning_count >= max_for_warning:
                reason = result.strip()[4:].strip()
                print(f"Đoạn code có khả năng có lỗ hổng bảo mật! \n{reason}")
                return

    print("Đoạn code không có lỗ hổng bảo mật rõ ràng.")

if __name__ == "__main__":
    code_snippet = """<?php
        $username = $_POST['username'];
        $password = $_POST['password'];

        // LỖ HỔNG Ở ĐÂY: Nối chuỗi trực tiếp dữ liệu người dùng vào câu truy vấn SQL
        $sql = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";

        $result = $conn->query($sql);

        if ($result->num_rows > 0) {
            echo "Đăng nhập thành công!";
        } else {
            echo "Sai tài khoản hoặc mật khẩu.";
        }
        ?>
    """
    pipeline(code_snippet)

    
