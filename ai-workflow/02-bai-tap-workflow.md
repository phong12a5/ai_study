# Bài tập AI Workflow — Thực hành tăng dần

> Cách học: làm theo thứ tự. Mỗi bài có **mục tiêu**, **đề bài**, **gợi ý**, và **tiêu chí đạt**.
> Đáp án mẫu nằm trong thư mục `solutions/`. **Tự làm trước, xem sau.**

## Chuẩn bị môi trường

```bash
pip install openai anthropic          # cài cái nào bạn dùng cũng được
export OPENAI_API_KEY="sk-..."        # nếu dùng OpenAI
# hoặc: export ANTHROPIC_API_KEY="sk-ant-..."

# (tùy chọn) chọn nhà cung cấp mặc định; nếu bỏ qua sẽ tự dò theo key đang có:
export LLM_PROVIDER=openai            # hoặc "anthropic"
```

Dùng hàm `llm()` chung trong file **`llm.py`** (đã tạo sẵn). Hàm này **provider-agnostic**:
gọi bằng **tier** thay vì model id cụ thể, nên code bài tập chạy được dù bạn xài key nào.

```python
from llm import llm

llm("xin chào")                  # tier mặc định "balanced"
llm("việc khó", model="strong")  # tier: cheap | balanced | strong
llm("...", model="gpt-4o-mini")  # vẫn nhận model id cụ thể nếu muốn
```

| tier | OpenAI | Anthropic | dùng khi |
|---|---|---|---|
| `cheap` | gpt-4o-mini | claude-haiku-4-5 | việc đơn giản (phân loại, định tuyến) |
| `balanced` | gpt-4o | claude-sonnet-4-6 | mặc định |
| `strong` | gpt-4o | claude-opus-4-8 | việc khó (suy luận, code phức tạp) |

> Test nhanh hàm: `python llm.py`. Muốn đổi model strong của OpenAI sang dòng suy luận
> (vd `o3`) thì sửa bảng `TIERS` trong `llm.py`.

---

## Bài 0 — Viên gạch nền (Augmented LLM)
**Mục tiêu:** quen với việc gọi LLM và buộc nó trả về định dạng kiểm soát được.

**Đề:** Viết hàm `phan_loai_cam_xuc(text)` trả về đúng một trong: `TICH_CUC`, `TIEU_CUC`, `TRUNG_TINH`. Test với 5 câu tiếng Việt.

**Gợi ý:** Trong system prompt yêu cầu "chỉ trả về đúng một nhãn, không giải thích". Strip kết quả.

**Đạt khi:** 5/5 câu trả về đúng nhãn, không lẫn chữ thừa.

---

## Bài 1 — Prompt Chaining
**Mục tiêu:** nối nhiều bước, có gate kiểm tra.

**Đề:** Xây pipeline tạo email marketing:
1. Bước 1: từ mô tả sản phẩm → sinh **3 ý chính** (bullet).
2. **Gate:** kiểm tra có đúng 3 ý không; nếu không, sinh lại (tối đa 2 lần).
3. Bước 2: từ 3 ý → viết email hoàn chỉnh (tiêu đề + thân).

**Gợi ý:** Đếm số dòng bullet bằng code, không hỏi LLM. Gate là logic Python.

**Đạt khi:** Chạy với 2 sản phẩm khác nhau đều ra email hợp lý; gate thực sự chặn được trường hợp sai số lượng ý.

---

## Bài 2 — Routing
**Mục tiêu:** phân loại rồi xử lý chuyên biệt + tối ưu chi phí.

**Đề:** Hệ thống hỏi đáp định tuyến câu hỏi thành 3 loại: `TOAN` (giải toán), `CODE` (viết code), `CHUNG`.
- `TOAN` và `CODE` → dùng tier `strong` (mạnh).
- `CHUNG` → dùng tier `cheap` (rẻ, nhanh).

In ra loại đã chọn + model đã dùng cho mỗi câu.

**Gợi ý:** Router là 1 lần gọi LLM trả về đúng 1 nhãn. Map nhãn → (system prompt, model).

**Đạt khi:** 6 câu test (2 mỗi loại) đều route đúng và dùng đúng model.

---

## Bài 3 — Parallelization (Sectioning)
**Mục tiêu:** chạy song song nhiều việc độc lập rồi tổng hợp.

**Đề:** Cho một đoạn review sản phẩm, đồng thời (song song) trích xuất:
- (A) Điểm tốt
- (B) Điểm xấu
- (C) Có chứa ngôn từ độc hại không (YES/NO)

Sau đó tổng hợp thành 1 JSON: `{"tot": [...], "xau": [...], "doc_hai": "YES/NO"}`.

**Gợi ý:** Dùng `concurrent.futures.ThreadPoolExecutor` để gọi 3 LLM song song. Mỗi việc là 1 prompt riêng.

**Đạt khi:** Kết quả là JSON hợp lệ và 3 phần được gọi đồng thời (đo thời gian: song song nhanh hơn tuần tự rõ rệt).

---

## Bài 4 — Parallelization (Voting)
**Mục tiêu:** tăng độ tin cậy bằng bỏ phiếu.

**Đề:** Viết `kiem_tra_lo_hong(code)` chạy LLM **5 lần** hỏi "đoạn code này có lỗ hổng bảo mật không? YES/NO + lý do". Lấy theo đa số. Nếu ≥3 phiếu YES → cảnh báo.

**Gợi ý:** Đặt nhiệt độ (temperature) cao hơn chút để các lần đa dạng. Đếm phiếu bằng code.

**Đạt khi:** Với code có lỗ hổng (vd SQL injection) hệ thống cảnh báo; với code sạch thì không.

---

## Bài 5 — Orchestrator–Workers
**Mục tiêu:** phân rã task ĐỘNG (số lượng không biết trước).

**Đề:** Nhập một chủ đề bài nghiên cứu. Orchestrator tự quyết chia thành N mục con (vd 3–6 mục tùy chủ đề), trả về danh sách mục. Mỗi mục giao cho 1 worker viết 1 đoạn. Synthesizer ghép thành bài hoàn chỉnh có mở bài/kết bài.

**Gợi ý:** Orchestrator trả về JSON danh sách tiêu đề mục → parse → loop worker. Đây là điểm khác parallelization: **N do LLM quyết**, không hard-code.

**Đạt khi:** 2 chủ đề khác nhau cho ra số mục khác nhau, bài ghép mạch lạc.

---

## Bài 6 — Evaluator–Optimizer
**Mục tiêu:** vòng lặp tạo–đánh giá–cải thiện.

**Đề:** Viết `dich_va_toi_uu(cau_tieng_anh)`:
1. Generator dịch sang tiếng Việt.
2. Evaluator chấm theo tiêu chí: tự nhiên, đúng nghĩa, đúng sắc thái → trả `ĐẠT` hoặc góp ý.
3. Lặp tối đa 3 vòng. In ra từng vòng để thấy bản dịch tiến bộ.

**Gợi ý:** Generator và Evaluator nên là 2 prompt/persona khác nhau. Dừng sớm khi `ĐẠT`.

**Đạt khi:** Với câu có thành ngữ/đa nghĩa, bản dịch vòng sau tốt hơn vòng đầu một cách thấy được; log in rõ từng vòng.

---

## Bài 7 — Tổng hợp (Capstone)
**Mục tiêu:** kết hợp nhiều mẫu thành 1 hệ thống thật.

**Đề:** Xây "Trợ lý xử lý phản hồi khách hàng":
1. **Routing**: phân loại phản hồi (KHIẾU_NẠI / HỎI_ĐÁP / GÓP_Ý).
2. Với KHIẾU_NẠI → **Parallelization**: song song (a) đánh giá mức độ nghiêm trọng, (b) soạn câu trả lời xoa dịu.
3. Câu trả lời đi qua **Evaluator–Optimizer**: đảm bảo lịch sự + giải quyết được vấn đề trước khi xuất.
4. In ra log mỗi bước để minh bạch.

**Đạt khi:** Chạy được end-to-end trên 3 phản hồi mẫu khác loại; log cho thấy đúng các mẫu workflow được dùng đúng chỗ.

---

## Checklist hoàn thành

- [ ] Bài 0 — Augmented LLM
- [ ] Bài 1 — Prompt Chaining
- [ ] Bài 2 — Routing
- [ ] Bài 3 — Parallelization (sectioning)
- [ ] Bài 4 — Parallelization (voting)
- [ ] Bài 5 — Orchestrator–Workers
- [ ] Bài 6 — Evaluator–Optimizer
- [ ] Bài 7 — Capstone

> Làm xong Bài 7 là bạn đã nắm chắc workflow. Buổi sau ta chuyển sang **AI Agent** (luồng tự quyết, tool use, vòng lặp agentic).
