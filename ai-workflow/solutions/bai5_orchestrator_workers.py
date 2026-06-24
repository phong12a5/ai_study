"""Bài 5 — Orchestrator–Workers: số mục con do LLM tự quyết (động).
Chạy: python solutions/bai5_orchestrator_workers.py
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm import llm


def orchestrate(chu_de):
    """Orchestrator tự quyết chia thành mấy mục, trả về list tiêu đề."""
    raw = llm(
        f"Chủ đề bài nghiên cứu: {chu_de}\n"
        "Hãy chia thành các mục con hợp lý (số lượng tùy chủ đề, 3-6 mục). "
        'Chỉ trả về JSON dạng: {"muc": ["tiêu đề 1", "tiêu đề 2", ...]}',
        model="strong",
    )
    raw = re.search(r"\{.*\}", raw, re.S).group(0)  # lấy phần JSON
    return json.loads(raw)["muc"]


def worker(chu_de, tieu_de_muc):
    return llm(f"Trong bài về '{chu_de}', viết một đoạn cho mục: '{tieu_de_muc}'.")


def synthesize(chu_de, doan_list):
    than = "\n\n".join(f"## {t}\n{n}" for t, n in doan_list)
    return llm(
        f"Đây là các mục của bài '{chu_de}':\n{than}\n\n"
        "Thêm mở bài và kết bài để thành bài hoàn chỉnh, mạch lạc.",
        model="strong", max_tokens=2048,
    )


def run(chu_de):
    muc = orchestrate(chu_de)
    print(f"[orchestrator] '{chu_de}' -> {len(muc)} mục: {muc}")
    doan_list = [(t, worker(chu_de, t)) for t in muc]   # có thể song song hóa
    return synthesize(chu_de, doan_list)


if __name__ == "__main__":
    for cd in ["Tác động của AI tới giáo dục", "Lịch sử cà phê Việt Nam"]:
        print("=" * 60)
        print(run(cd))
