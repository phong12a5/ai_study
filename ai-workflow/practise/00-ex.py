import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from llm import llm

def phan_loai_cam_xuc(text):
    prompt = f"Phân loại cảm xúc của đoạn văn sau: '{text}'. Chỉ trả về một từ duy nhất là 'TICH_CUC', 'TIEU_CUC' hoặc 'TRUNG_TINH'."
    return llm(prompt, model="cheap", provider="openai")

if __name__ == "__main__":
    text = "Tôi rất vui khi được gặp bạn hôm nay!"
    cam_xuc = phan_loai_cam_xuc(text)
    print(f"Cảm xúc của đoạn văn: {cam_xuc}")