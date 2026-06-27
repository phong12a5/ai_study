"""Lõi RAG: chunking + VectorStore (numpy) + Naive RAG có dẫn nguồn + chống bịa.
Bao trùm R1, R2, R3, R4. Chạy: python solutions/mini_rag.py
Cài: pip install openai numpy ; export OPENAI_API_KEY=sk-...
"""
import numpy as np
from openai import OpenAI

client = OpenAI()
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"


# ---------- Embedding ----------
def embed(texts: list[str]) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return np.array([d.embedding for d in resp.data], dtype=np.float32)


# ---------- R1: Chunking (trượt cửa sổ, có overlap) ----------
def chunk(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size].strip()]


# ---------- R2: Vector Store ----------
class VectorStore:
    def __init__(self):
        self.texts: list[str] = []
        self.sources: list[str] = []
        self.vecs: np.ndarray | None = None      # (n, d), đã chuẩn hóa L2

    def add(self, chunks: list[str], source: str = ""):
        v = embed(chunks)
        v /= np.linalg.norm(v, axis=1, keepdims=True)   # chuẩn hóa -> cosine = tích vô hướng
        self.vecs = v if self.vecs is None else np.vstack([self.vecs, v])
        self.texts += chunks
        self.sources += [source] * len(chunks)

    def search(self, query: str, k: int = 3) -> list[tuple[str, str, float]]:
        q = embed([query])[0]
        q /= np.linalg.norm(q)
        scores = self.vecs @ q                          # cosine với mọi chunk
        idx = np.argsort(-scores)[:k]
        return [(self.texts[i], self.sources[i], float(scores[i])) for i in idx]


# ---------- R3 + R4: Naive RAG có dẫn nguồn + chống bịa ----------
def rag_answer(store: VectorStore, question: str, k: int = 3) -> str:
    hits = store.search(question, k)
    context = "\n\n".join(f"[Nguồn: {src or '?'}]\n{txt}" for txt, src, _ in hits)
    prompt = (
        "Chỉ dựa vào CONTEXT dưới đây để trả lời. "
        "Nếu CONTEXT không chứa câu trả lời, hãy nói đúng câu: "
        "'Tôi không tìm thấy thông tin này trong tài liệu.' — KHÔNG được bịa.\n\n"
        f"CONTEXT:\n{context}\n\nCÂU HỎI: {question}"
    )
    resp = client.chat.completions.create(
        model=CHAT_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0)
    answer = resp.choices[0].message.content.strip()
    nguon = ", ".join(sorted({src for _, src, _ in hits if src}))
    return f"{answer}\n\n(Đoạn tham chiếu từ: {nguon or 'n/a'})"


# ---------- Demo ----------
if __name__ == "__main__":
    tai_lieu = (
        "Trần Văn A sinh năm 1990 tại Huế. Anh tốt nghiệp Đại học Bách Khoa năm 2012 "
        "ngành Công nghệ thông tin. Năm 2015 anh sáng lập công ty phần mềm Delta, "
        "chuyên về trí tuệ nhân tạo. Sở thích của anh là leo núi và chơi cờ vua. "
        "Năm 2020, công ty Delta đạt doanh thu 5 triệu USD và mở văn phòng tại Singapore."
    )

    store = VectorStore()
    store.add(chunk(tai_lieu, size=120, overlap=20), source="tieu_su_A.txt")

    for q in [
        "Trần Văn A sinh năm nào?",
        "Công ty Delta làm về lĩnh vực gì?",
        "Trần Văn A có mấy người con?",        # KHÔNG có trong tài liệu -> phải nói không biết
    ]:
        print("=" * 60)
        print("HỎI:", q)
        print(rag_answer(store, q))
