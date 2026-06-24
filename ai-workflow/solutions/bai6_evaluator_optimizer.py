"""Bài 6 — Evaluator–Optimizer: vòng lặp dịch → chấm → cải thiện.
Chạy: python solutions/bai6_evaluator_optimizer.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm import llm


def generator(cau_en, gop_y=None):
    p = f"Dịch câu sau sang tiếng Việt tự nhiên:\n{cau_en}"
    if gop_y:
        p += f"\n\nCải thiện theo góp ý của người biên tập:\n{gop_y}"
    return llm(p, system="Bạn là dịch giả tiếng Việt giỏi, ưu tiên tự nhiên và đúng sắc thái.")


def evaluator(cau_en, ban_dich):
    return llm(
        f"Câu gốc (EN): {cau_en}\nBản dịch (VI): {ban_dich}\n\n"
        "Chấm theo: đúng nghĩa, tự nhiên, đúng sắc thái. "
        "Nếu tốt, trả về đúng chữ 'ĐẠT'. Nếu chưa, nêu góp ý cụ thể để sửa.",
        system="Bạn là biên tập viên khó tính.",
    )


def dich_va_toi_uu(cau_en, max_vong=3):
    ban_dich = generator(cau_en)
    for vong in range(1, max_vong + 1):
        print(f"\n[Vòng {vong}] {ban_dich}")
        nhan_xet = evaluator(cau_en, ban_dich)
        if "ĐẠT" in nhan_xet.upper():
            print("  -> Evaluator: ĐẠT, dừng.")
            break
        print(f"  -> Góp ý: {nhan_xet}")
        ban_dich = generator(cau_en, gop_y=nhan_xet)
    return ban_dich


if __name__ == "__main__":
    cau = "It's raining cats and dogs, so let's call it a day."
    print("\nKẾT QUẢ CUỐI:", dich_va_toi_uu(cau))
