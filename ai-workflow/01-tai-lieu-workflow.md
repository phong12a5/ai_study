# AI Workflow — Tài liệu học nhanh

> Mục tiêu: Sau tài liệu này bạn hiểu rõ **workflow là gì**, phân biệt với **agent**, nắm **5 mẫu workflow kinh điển**, và biết **chọn mẫu nào cho bài toán nào**.

---

## 0. Bức tranh tổng quan

Khi xây dựng hệ thống dùng LLM, có một phổ (spectrum) từ đơn giản đến phức tạp:

```
LLM gọi đơn lẻ  →  Workflow (luồng cố định)  →  Agent (luồng tự quyết)
   (đơn giản)                                        (phức tạp)
```

**Nguyên tắc vàng:** Luôn dùng giải pháp ĐƠN GIẢN NHẤT có thể giải quyết được bài toán.
Đừng dùng agent khi một prompt đơn lẻ là đủ. Đừng dùng workflow khi một lần gọi LLM là đủ.

---

## 1. Workflow vs Agent — khác nhau ở đâu?

| | **Workflow** | **Agent** |
|---|---|---|
| Luồng đi | **Cố định**, lập trình viên định nghĩa trước bằng code | **Động**, LLM tự quyết các bước tiếp theo |
| Dự đoán | Dễ đoán, dễ test, chi phí ổn định | Khó đoán, chi phí biến động |
| Kiểm soát | Cao | Thấp hơn (đánh đổi lấy linh hoạt) |
| Khi nào dùng | Bài toán có các bước rõ ràng, lặp lại được | Bài toán mở, số bước không biết trước |

**Định nghĩa ngắn gọn (theo Anthropic):**
- **Workflow**: hệ thống trong đó LLM và tool được điều phối qua **các đường code định sẵn**.
- **Agent**: hệ thống trong đó LLM **tự định hướng** quá trình của chính nó, tự chọn tool và số bước.

> 💡 Phần lớn ứng dụng thực tế thành công đều là **workflow**, không phải agent. Agent chỉ thắng khi tính linh hoạt và tự quyết là bắt buộc.

---

## 2. Khối nền tảng: "Augmented LLM"

Mọi workflow đều xây trên một viên gạch cơ bản: **LLM được tăng cường** (augmented LLM) — tức một LLM có thêm:

- **Retrieval** (truy xuất dữ liệu/tài liệu)
- **Tools** (gọi hàm, API bên ngoài)
- **Memory** (nhớ ngữ cảnh giữa các bước)

```
            ┌─────────────┐
  Input ──▶ │             │ ──▶ Output
            │     LLM     │
            │  + Retrieval│
            │  + Tools    │
            │  + Memory   │
            └─────────────┘
```

Trước khi học các mẫu phức tạp, hãy đảm bảo bạn thành thạo viên gạch này: cho LLM gọi tool, đọc tài liệu, và giữ ngữ cảnh.

---

## 3. NĂM MẪU WORKFLOW KINH ĐIỂN

### 3.1. Prompt Chaining (Nối chuỗi prompt)

Chia một việc lớn thành **chuỗi các bước tuần tự**, output của bước trước là input của bước sau.

```
Input ──▶ [LLM 1] ──▶ [LLM 2] ──▶ [LLM 3] ──▶ Output
                          ▲
                      (có thể chèn "gate":
                       kiểm tra rồi mới đi tiếp)
```

**Khi nào dùng:** việc có thể tách thành các bước cố định, rõ ràng. Đổi độ trễ (chậm hơn) lấy độ chính xác (mỗi bước dễ hơn).

**Ví dụ thực tế:**
- Viết outline → kiểm tra outline đạt tiêu chí → viết bài đầy đủ.
- Dịch tài liệu → kiểm tra ngữ pháp → đánh bóng văn phong.

**Gate (cổng kiểm tra):** giữa các bước có thể thêm một check bằng code: nếu output bước trước không đạt → dừng hoặc xử lý lại.

---

### 3.2. Routing (Định tuyến / Phân loại)

Một LLM **phân loại** input, rồi chuyển đến **luồng xử lý chuyên biệt** phù hợp.

```
                ┌──▶ [Xử lý loại A]
Input ──▶ [Router] ──▶ [Xử lý loại B]
                └──▶ [Xử lý loại C]
```

**Khi nào dùng:** input có nhiều loại khác nhau, mỗi loại nên xử lý riêng (prompt riêng, model riêng).

**Ví dụ thực tế:**
- Chăm sóc khách hàng: phân loại câu hỏi (hoàn tiền / kỹ thuật / chung) → route đến prompt chuyên biệt.
- Tiết kiệm chi phí: câu dễ → model nhỏ/rẻ; câu khó → model mạnh.

---

### 3.3. Parallelization (Song song hóa)

Chạy nhiều LLM **đồng thời** rồi tổng hợp kết quả. Có 2 biến thể:

**a) Sectioning** — chia việc thành các phần độc lập, chạy song song:
```
         ┌──▶ [LLM phần 1] ──┐
Input ──▶├──▶ [LLM phần 2] ──┤──▶ [Aggregator] ──▶ Output
         └──▶ [LLM phần 3] ──┘
```

**b) Voting** — chạy CÙNG một việc nhiều lần để tăng độ tin cậy:
```
         ┌──▶ [LLM lần 1] ──┐
Input ──▶├──▶ [LLM lần 2] ──┤──▶ [Lấy đa số/đồng thuận] ──▶ Output
         └──▶ [LLM lần 3] ──┘
```

**Khi nào dùng:**
- Sectioning: các phần xử lý độc lập nhau (vd: vừa kiểm duyệt nội dung vừa trả lời).
- Voting: cần độ tin cậy cao (vd: review code có lỗ hổng bảo mật — chạy nhiều lần, lỗi nào nhiều phiếu thì cảnh báo).

---

### 3.4. Orchestrator–Workers (Điều phối viên – Thợ)

Một LLM **trung tâm (orchestrator)** phân rã việc động thành các task con, giao cho các **worker LLM**, rồi tổng hợp.

```
                 ┌──▶ [Worker 1] ──┐
Input ──▶ [Orchestrator] ──▶ [Worker 2] ──┤──▶ [Synthesizer] ──▶ Output
                 └──▶ [Worker N] ──┘
        (tự quyết cần bao nhiêu worker)
```

**Khác Parallelization ở đâu?** Ở parallelization, số phần được **định sẵn bằng code**. Ở đây, orchestrator **tự quyết** cần chia thành mấy task tùy input → linh hoạt hơn, gần với agent hơn.

**Ví dụ thực tế:**
- Sửa code trên nhiều file: orchestrator quyết file nào cần sửa, giao mỗi file cho 1 worker.
- Tổng hợp thông tin từ nhiều nguồn không biết trước số lượng.

---

### 3.5. Evaluator–Optimizer (Đánh giá – Tối ưu lặp)

Một LLM tạo kết quả, một LLM khác **đánh giá và phản hồi**, lặp lại đến khi đạt.

```
Input ──▶ [Generator] ──▶ kết quả ──▶ [Evaluator]
              ▲                            │
              │      "chưa đạt + góp ý"    │
              └────────────────────────────┘
                       (lặp)
                            │ "đạt"
                            ▼
                         Output
```

**Khi nào dùng:** khi có **tiêu chí đánh giá rõ ràng** VÀ phản hồi lặp giúp cải thiện thấy rõ — giống cách con người viết → sửa → viết lại.

**Ví dụ thực tế:**
- Dịch văn học: dịch → đánh giá sắc thái → dịch lại tốt hơn.
- Tìm kiếm nhiều vòng: tìm → đánh giá đủ thông tin chưa → tìm tiếp.

---

## 4. Bảng tra nhanh "Chọn mẫu nào?"

| Tình huống | Mẫu nên dùng |
|---|---|
| Việc tách được thành các bước cố định, tuần tự | **Prompt Chaining** |
| Input nhiều loại, mỗi loại xử lý khác nhau | **Routing** |
| Nhiều phần độc lập, muốn nhanh | **Parallelization (sectioning)** |
| Cần độ tin cậy cao, muốn "bỏ phiếu" | **Parallelization (voting)** |
| Số task con không biết trước, cần chia động | **Orchestrator–Workers** |
| Có tiêu chí rõ, cần lặp để hoàn thiện | **Evaluator–Optimizer** |
| Việc mở hoàn toàn, không đoán được luồng | (cân nhắc) **Agent** |

---

## 5. Nguyên tắc thiết kế (rất quan trọng)

1. **Đơn giản trước** — chỉ tăng độ phức tạp khi kết quả thực sự tốt hơn.
2. **Minh bạch** — cho thấy rõ LLM đang "nghĩ" và làm gì ở mỗi bước (dễ debug).
3. **Tài liệu hóa tool tốt** — nếu có dùng tool, mô tả tool rõ ràng như viết tài liệu cho người.
4. **Đo lường** — luôn có cách đánh giá kết quả (eval) trước khi tối ưu.
5. **Đừng vội agent hóa** — workflow giải quyết được phần lớn bài toán với chi phí và độ phức tạp thấp hơn nhiều.

---

## 6. Pseudocode mẫu (để hình dung code)

```python
# Viên gạch: gọi LLM với Claude API
from anthropic import Anthropic
client = Anthropic()

def llm(prompt: str, system: str = "") -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-6",     # model nhanh, cân bằng — đổi sang claude-opus-4-8 khi cần mạnh hơn
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text

# 1. PROMPT CHAINING
def chain(topic):
    outline = llm(f"Viết outline cho bài về: {topic}")
    if "ĐẠT" not in llm(f"Outline này ổn chưa? Trả lời ĐẠT/CHƯA:\n{outline}"):
        return "Outline chưa đạt"
    return llm(f"Viết bài đầy đủ theo outline:\n{outline}")

# 2. ROUTING
def route(question):
    loai = llm(f"Phân loại câu hỏi thành HOAN_TIEN/KY_THUAT/CHUNG. Chỉ trả 1 từ:\n{question}")
    prompts = {
        "HOAN_TIEN": "Bạn là CSKH chuyên hoàn tiền. ",
        "KY_THUAT": "Bạn là kỹ sư hỗ trợ kỹ thuật. ",
        "CHUNG":    "Bạn là trợ lý chung. ",
    }
    return llm(question, system=prompts.get(loai.strip(), prompts["CHUNG"]))

# 5. EVALUATOR-OPTIMIZER
def optimize(task, max_loops=3):
    result = llm(task)
    for _ in range(max_loops):
        feedback = llm(f"Đánh giá kết quả. Nếu đạt ghi 'ĐẠT'. Nếu chưa, góp ý cụ thể:\n{result}")
        if "ĐẠT" in feedback:
            break
        result = llm(f"Cải thiện kết quả dựa trên góp ý.\nKết quả cũ:\n{result}\nGóp ý:\n{feedback}")
    return result
```

---

## 7. Tự kiểm tra hiểu bài (trả lời nhanh trong đầu)

1. Khác biệt cốt lõi giữa workflow và agent là gì?
2. Khi nào nên dùng Routing thay vì nhét tất cả vào 1 prompt?
3. Parallelization-voting khác Orchestrator–Workers ở điểm nào?
4. "Gate" trong prompt chaining để làm gì?
5. Evaluator–Optimizer cần điều kiện gì để hiệu quả?

> Đáp án nằm rải rác trong tài liệu — quay lại đối chiếu nếu chưa chắc.

Tiếp theo: mở file `02-bai-tap-workflow.md` để thực hành.
