import sys
from pathlib import Path
import concurrent.futures

sys.path.append(str(Path(__file__).parent.parent))
from llm import llm

def translate(phase, feedback=None):
    p = f"Dịch sang tiếng Việt: {phase}"
    if feedback:
        p += f"\nBản dịch trước bị chê, sửa theo góp ý:\n{feedback}"   # 🔑 đưa feedback vào
    return llm(p)

def eval(original, translated):
    prompt = f"Dựa vào tiêu chí: tự nhiên, đúng nghĩa và đúng sắc, đánh giá sự chính xác của bản dịch sau bằng cách trả về duy nhất 'ĐẠT' hoặc 'KHÔNG ĐẠT (Lí do)': '{translated}' so với bản gốc: '{original}'"
    result = llm(prompt, model="cheap", provider="openai")
    return result

def pipeline(phase):
    last_feedback = None
    for i in range(3):
    
        translated = translate(phase, feedback=last_feedback)
        print(f"Translated: {translated}")

        evaluation = eval(phase, translated)
        print(f"Evaluation: {evaluation}")
        if evaluation.strip().upper() == "ĐẠT":
            print("Translation is acceptable.")
            return
        else:
            print("Translation is not acceptable. Generating a new translation...")
            last_feedback = evaluation.strip().substring(len("KHÔNG ĐẠT (Lí do):")).strip()  # Extract the reason for failure
            print(f"Feedback for improvement: {last_feedback}")

    print("Translation is not acceptable after 3 attempts.")
    return



if __name__ == "__main__":
    subject = "What is the impact of artificial intelligence on society?"
    pipeline(subject)
