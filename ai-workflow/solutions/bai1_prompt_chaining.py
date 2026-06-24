"""Bài 1 — Prompt Chaining với gate kiểm tra số lượng ý.
Chạy: python solutions/bai1_prompt_chaining.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm import llm


def sinh_3_y(mo_ta):
    return llm(
        f"Sản phẩm: {mo_ta}\n"
        "Hãy nêu ĐÚNG 3 ý chính bán hàng, mỗi ý 1 dòng bắt đầu bằng '- '. "
        "Không thêm gì khác."
    )


def dem_bullet(text):
    return sum(1 for d in text.splitlines() if d.strip().startswith("-"))


def pipeline(mo_ta, max_thu=3):
    # Bước 1 + Gate: lặp tới khi đúng 3 ý
    for lan in range(max_thu):
        y = sinh_3_y(mo_ta)
        if dem_bullet(y) == 3:
            break
        print(f"[gate] Lần {lan+1}: sai số lượng ý, sinh lại...")
    else:
        raise RuntimeError("Không sinh được đúng 3 ý sau nhiều lần thử")

    # Bước 2: viết email từ 3 ý
    email = llm(
        f"Viết một email marketing (có 'Tiêu đề:' và thân email) dựa trên 3 ý sau:\n{y}"
    )
    return y, email


if __name__ == "__main__":
    for sp in ["Tai nghe chống ồn pin 40h", "Bình giữ nhiệt giữ lạnh 24h"]:
        print("=" * 60, "\nSản phẩm:", sp)
        y, email = pipeline(sp)
        print("\n-- 3 ý --\n", y, "\n\n-- Email --\n", email)
