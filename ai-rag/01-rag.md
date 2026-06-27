# RAG — Retrieval-Augmented Generation (Lý thuyết + Bài tập)

> Mục tiêu: hiểu RAG từ gốc và **tự xây một hệ RAG hoàn chỉnh bằng Python thuần** (embedding → vector store → retrieve → trả lời có dẫn nguồn), rồi nối nó vào Agent bạn đã viết.
> Tiền đề: bạn đã làm chủ workflow, tool/agent, MCP. RAG là cách cấp cho LLM **kiến thức riêng / cập nhật** mà nó không được huấn luyện.

---

# PHẦN I — LÝ THUYẾT

## 1. Vấn đề RAG giải quyết

LLM có 4 giới hạn cố hữu:
1. **Knowledge cutoff** — không biết sự kiện sau ngày huấn luyện.
2. **Không biết dữ liệu riêng của bạn** — tài liệu nội bộ, code, ghi chú.
3. **Bịa (hallucinate)** — khi không biết, nó "chế" ra câu trả lời nghe hợp lý.
4. **Context window có hạn** — không thể nhét cả 10.000 trang vào prompt.

**RAG** = trước khi trả lời, **truy xuất (retrieve)** những đoạn tài liệu liên quan nhất rồi **nhét vào prompt** để LLM trả lời *dựa trên* chúng.

```
Câu hỏi → [tìm đoạn liên quan trong kho tài liệu] → nhét vào prompt → LLM trả lời có căn cứ
```

> 🔑 Tư tưởng cốt lõi: thay vì bắt LLM "nhớ", ta để nó "tra cứu rồi đọc". Giống đưa cho người thông minh đúng trang sách cần thiết trước khi hỏi.

## 2. Pipeline RAG — 2 pha

**Pha A — Indexing (làm trước, offline):** chuẩn bị kho tri thức.
```
Tài liệu → [Chunk: cắt nhỏ] → [Embed: vector hóa] → [Lưu vào Vector Store]
```

**Pha B — Retrieval + Generation (lúc hỏi, online):**
```
Câu hỏi → [Embed câu hỏi] → [Tìm k đoạn gần nhất trong store] → [Nhét vào prompt] → [LLM trả lời]
```

```
        ┌──────────────────── PHA A: INDEXING (offline) ────────────────────┐
        │  docs → chunk → embed → ┌─────────────┐                            │
        │                         │ Vector Store│                            │
        └─────────────────────────┤  (vectors)  ├────────────────────────────┘
                                   └──────┬──────┘
        ┌──────────────────── PHA B: ││ truy vấn ─────────────────────────────┐
        │  query → embed query → tìm top-k gần nhất → [đoạn 1..k] ─┐          │
        │                                                          ▼          │
        │                                    prompt = câu hỏi + đoạn → LLM → trả lời
        └────────────────────────────────────────────────────────────────────┘
```

## 3. Bốn khái niệm lõi

**a) Embedding** — biến văn bản thành **vector số** (vd 1536 chiều) sao cho **câu nghĩa gần nhau → vector gần nhau**. "mèo" và "chó" gần nhau hơn "mèo" và "ô tô". Đo độ gần bằng **cosine similarity** (1 = trùng hướng, 0 = không liên quan).

**b) Chunking** — cắt tài liệu dài thành đoạn nhỏ (vd 300–800 token), thường có **overlap** (chồng lấn) để không cắt ngang ý. Vì sao cần: embedding cả cuốn sách thành 1 vector thì "nhòe" nghĩa; và prompt chỉ nhét được vài đoạn.

**c) Vector store + similarity search** — kho lưu vector, cho phép tìm nhanh "k vector gần câu hỏi nhất". Học bằng numpy được; production dùng FAISS / Chroma / pgvector / Pinecone.

**d) Top-k retrieval** — lấy `k` đoạn liên quan nhất (vd k=3–5). Nhiều quá → nhiễu + tốn token; ít quá → thiếu thông tin.

## 4. "Naive RAG" và vì sao nó hay trật

Pipeline ở mục 2 là **Naive RAG** — chạy được nhưng hay lỗi:

| Lỗi thường gặp | Nguyên nhân | Cách cải thiện |
|---|---|---|
| Lấy nhầm đoạn không liên quan | embedding/chunk kém | chỉnh chunk size, **rerank** lại top-k |
| Bỏ sót đoạn dùng từ khóa lạ | chỉ search ngữ nghĩa | **hybrid search** (kết hợp keyword BM25 + vector) |
| Câu hỏi mơ hồ → tìm trật | query xấu | **query rewriting** (LLM viết lại câu hỏi trước khi tìm) |
| Trả lời bịa dù có context | prompt không ràng buộc | ép "chỉ trả lời dựa trên context, không có thì nói không biết" |
| Lấy đúng nhưng lẫn nguồn sai | thiếu lọc | **metadata filtering** (lọc theo nguồn/ngày) |

## 5. Đánh giá RAG (đừng bỏ qua)

Hai trục cần đo (giống tinh thần eval ở Agent):
- **Retrieval quality** — đoạn lấy về có chứa câu trả lời không? (recall@k)
- **Answer quality** —
  - **Faithfulness/Groundedness**: câu trả lời có *bám* vào context không, hay bịa?
  - **Relevance**: có trả lời đúng câu hỏi không?

Dùng được **LLM-as-judge** (đã học): cho một LLM chấm "câu trả lời này có được support bởi context không?".

## 6. RAG vs Fine-tuning vs Long-context — chọn cái nào?

| Nhu cầu | Giải pháp |
|---|---|
| Kiến thức **thay đổi thường xuyên**, cần dẫn nguồn | **RAG** ✅ |
| Dạy model **phong cách/định dạng/kỹ năng** mới | Fine-tuning |
| Tài liệu **nhỏ, vừa context** (vài chục trang) | Nhét thẳng (long-context), không cần RAG |
| Kho **lớn**, riêng tư, cập nhật liên tục | **RAG** ✅ |

> RAG thắng khi: dữ liệu lớn/riêng/hay đổi và cần **truy vết nguồn**. Đó là phần lớn ứng dụng doanh nghiệp.

## 7. Nối với Agent — Agentic RAG

Ở Naive RAG, ta **luôn** retrieve trước mỗi câu. Nhưng nhớ bài Agent: ta có thể biến **retrieval thành một TOOL**, để **LLM tự quyết khi nào cần tra cứu** (câu chào thì không tra, câu hỏi dữ kiện thì tra), thậm chí tra nhiều vòng.

```
Naive RAG:   luôn luôn  retrieve → answer            (workflow cố định)
Agentic RAG: LLM tự gọi tool `search_docs(query)`     (agent tự quyết)
             → có thể tra lại nhiều lần, tinh chỉnh query
```

→ Đây chính là chỗ 4 module của bạn hội tụ: **RAG = một tool tra cứu mà Agent của bạn gọi.**

---

# PHẦN II — BÀI TẬP

## Chuẩn bị
```bash
pip install openai numpy        # numpy để tự làm vector store, không cần DB ngoài
export OPENAI_API_KEY=sk-...
```

Helper embedding dùng chung (tạo `rag_lib.py`):
```python
import numpy as np
from openai import OpenAI
client = OpenAI()

def embed(texts: list[str]) -> np.ndarray:
    """Trả về ma trận (n, d) các vector embedding."""
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([d.embedding for d in resp.data], dtype=np.float32)

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
```

---

## Bài R0 — Embedding & độ tương đồng
**Mục tiêu:** cảm nhận "nghĩa gần → vector gần".

**Đề:** Embed 5 câu, vd: "Tôi nuôi một con mèo", "Chú chó rất dễ thương", "Giá xăng tăng mạnh", "Thú cưng trong nhà", "Lạm phát ảnh hưởng kinh tế". Tính cosine giữa **mọi cặp**, in ma trận. Xác nhận nhóm thú cưng gần nhau, nhóm kinh tế gần nhau, hai nhóm xa nhau.

**Đạt khi:** số liệu cosine phản ánh đúng trực giác ngữ nghĩa.

---

## Bài R1 — Chunking
**Mục tiêu:** cắt tài liệu thành chunk có overlap.

**Đề:** Viết `chunk(text, size=500, overlap=50)` cắt theo ký tự (hoặc theo từ) thành các đoạn ~`size`, mỗi đoạn chồng `overlap` với đoạn trước. Test trên một đoạn văn dài ~2000 ký tự.

**Gợi ý:** trượt cửa sổ: bắt đầu ở `i`, lấy `text[i:i+size]`, nhảy `i += size - overlap`.

**Đạt khi:** các chunk phủ hết văn bản, ranh giới có chồng lấn, không mất chữ.

---

## Bài R2 — Mini Vector Store 🧱
**Mục tiêu:** tự xây kho vector + tìm top-k (lõi của RAG).

**Đề:** Viết `class VectorStore`:
- `add(chunks: list[str])` — embed và lưu (giữ cả text gốc + vector).
- `search(query: str, k=3) -> list[(text, score)]` — embed query, tính cosine với mọi vector, trả `k` đoạn điểm cao nhất.

**Gợi ý:** lưu vectors thành một ma trận numpy; similarity = `vectors @ q` (sau khi chuẩn hóa) rồi `argsort`.

**Đạt khi:** nạp vài đoạn, hỏi một câu, store trả đúng đoạn liên quan nhất lên đầu.

---

## Bài R3 — Naive RAG end-to-end 🎯
**Mục tiêu:** ghép thành hệ hỏi-đáp có căn cứ.

**Đề:** Dùng R1+R2. Cho một tài liệu (vd tiểu sử một nhân vật / mô tả sản phẩm). Pipeline:
1. chunk → add vào store (indexing).
2. Nhận câu hỏi → `search` top-k → ghép context.
3. Gọi LLM với prompt: *"Chỉ dựa vào CONTEXT sau để trả lời. CONTEXT: {...}. Câu hỏi: {...}"*.
4. In câu trả lời **kèm đoạn nguồn** đã dùng.

**Đạt khi:** trả lời đúng theo tài liệu và chỉ ra được đoạn nguồn.

---

## Bài R4 — Chống bịa ("Tôi không biết")
**Mục tiêu:** giảm hallucginate khi không có dữ liệu.

**Đề:** Thêm vào prompt R3 ràng buộc: *"Nếu CONTEXT không chứa câu trả lời, hãy nói 'Tôi không tìm thấy thông tin này trong tài liệu' — KHÔNG được bịa."* Hỏi một câu **chắc chắn không có** trong tài liệu và xác nhận nó từ chối thay vì bịa.

**Đạt khi:** câu ngoài phạm vi → trả lời "không tìm thấy"; câu trong phạm vi → vẫn trả lời đúng.

---

## Bài R5 — Cải thiện retrieval
**Mục tiêu:** thấy chất lượng retrieval đổi kết quả.

**Đề:** Chọn MỘT cải tiến và đo trước/sau:
- **(a) Query rewriting**: dùng LLM viết lại câu hỏi rõ hơn trước khi search.
- **(b) Rerank**: lấy top-10 rồi nhờ LLM chọn lại 3 đoạn liên quan nhất.
- **(c) Metadata filter**: gắn nguồn/chủ đề cho chunk, lọc trước khi search.

**Đạt khi:** chỉ ra được một câu hỏi mà cải tiến giúp lấy đúng đoạn hơn so với naive.

---

## Bài R6 — Agentic RAG (nối với Agent) 🤝
**Mục tiêu:** biến retrieval thành tool cho Agent tự quyết.

**Đề:** Dùng lại `Agent` (từ module agent). Bọc `store.search` thành tool `search_docs(query: str)`. Cho agent một system prompt: "Khi cần dữ kiện, hãy gọi `search_docs` rồi trả lời dựa trên kết quả." Hỏi xen kẽ: câu chào (agent KHÔNG search) và câu hỏi dữ kiện (agent search).

**Đạt khi:** agent tự gọi `search_docs` đúng lúc, bỏ qua khi không cần.

---

## Capstone — Hỏi-đáp trên chính ghi chú học AI của bạn 🎓
**Mục tiêu:** RAG trên dữ liệu thật, hữu ích ngay.

**Đề:** Index các file `.md` trong `ai_study` (workflow/agent/mcp/rag) → xây RAG hỏi-đáp về chính những gì bạn đã học. Yêu cầu:
1. Đọc & chunk tất cả `.md` (gắn metadata = tên file làm nguồn).
2. Trả lời có **trích nguồn** (file nào).
3. Có xử lý "không biết" (R4).
4. (Tùy chọn) bọc thành tool cho Agent (R6) hoặc thành **MCP server** `search_docs` để cắm vào Claude Code!

**Kịch bản:** hỏi *"Sự khác nhau giữa workflow và agent là gì?"* → RAG lấy đúng đoạn trong `01-tai-lieu-workflow.md` và trả lời kèm nguồn.

**Đạt khi:** chạy end-to-end trên tài liệu thật, trả lời đúng + dẫn nguồn + biết nói "không có".

---

## Tự kiểm tra
1. Hai pha của RAG là gì? Pha nào làm trước (offline)?
2. Vì sao phải chunk thay vì embed cả tài liệu thành 1 vector?
3. Cosine similarity đo điều gì?
4. Naive RAG khác Agentic RAG ở điểm nào?
5. Khi nào chọn RAG thay vì fine-tuning?

## Checklist
- [ ] R0 — Embedding & cosine
- [ ] R1 — Chunking
- [ ] R2 — Mini Vector Store 🧱
- [ ] R3 — Naive RAG end-to-end 🎯
- [ ] R4 — Chống bịa
- [ ] R5 — Cải thiện retrieval
- [ ] R6 — Agentic RAG 🤝
- [ ] Capstone — RAG trên ghi chú của bạn

> Xong Capstone: bạn đã đi trọn **Workflow → Tool/Agent → MCP → RAG** — đủ bộ kỹ năng xây một ứng dụng AI thực tế hoàn chỉnh.
> Lời giải lõi (vector store + naive RAG): `solutions/mini_rag.py`.
