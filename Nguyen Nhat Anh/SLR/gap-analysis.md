# GAP Analysis - Mutation Testing Optimization

**Evidence table: N = 5 papers | Ngày: 2026-06-08**

## Bảng Phân Tích Khoảng Trống (GAP)
| Cột / Phân loại | Hiện trạng từ Evidence Table (Pain Point) | Khoảng trống cốt lõi (GAP) |
|:---|:---|:---|
| **Công nghệ (GAP-T)** | Các tool hiện tại áp dụng toán tử đột biến một cách tĩnh (static rules) và đồng loạt trên diện rộng. | Chưa có giải pháp tích hợp LLM để phân tích ngữ cảnh (context-aware) nhằm tự động lọc bộ toán tử tối ưu đầu vào. |
| **Dữ liệu (GAP-D)** | Dataset cũ (Defects4J, MNIST) chỉ đo độ bao phủ thô, không phân tách các vùng code quan trọng. | Thiếu bộ dữ liệu kiểm thử được gắn nhãn theo vùng ngữ cảnh (critical paths). |
| **Metric (GAP-M)** | Các nghiên cứu chỉ tập trung tối đa hóa Mutation Score (MS) một cách cực đoan. | Thiếu cơ chế đánh giá sự cân bằng (trade-off) giữa Mutation Score và Chi phí thực thi. |
| **Hạn chế (GAP-S)** | Sinh ra quá nhiều mutant dư thừa hoặc tương đương (equivalent mutants) không thể bị tiêu diệt. | Bùng nổ chi phí thời gian và lãng phí tài nguyên thực nghiệm mà chưa được giải quyết. |

## GAP Chính được chọn: [GAP-T] - Khoảng trống Công nghệ
Các framework hiện tại (DeepMutation++, DeepCrime) sử dụng các toán tử đột biến tĩnh (static rules) áp dụng một cách mù quáng. **Chưa có giải pháp nào sử dụng LLM để tối ưu hóa và lọc tập toán tử dựa trên ngữ cảnh mã nguồn (context-aware).** Điều này dẫn đến việc sinh ra hàng loạt mutant dư thừa, làm bùng nổ chi phí và thời gian thực thi thực nghiệm. Giải pháp đề xuất của chúng tôi là xây dựng một bộ lọc thông minh (Context-aware Filter) bằng LLM để cắt tỉa các đột biến vô nghĩa ngay từ đầu.

## Kiểm tra phản chứng (Falsification Check)
*Xác nhận GAP-T thực sự tồn tại và chưa bị giải quyết bởi 5 nghiên cứu trong bảng:*
- **Paper 1 (Dakhel 2023 - MuTAP):** Có dùng LLM nhưng là để sinh test case (đầu ra), còn bộ toán tử đột biến vẫn lấy nguyên bản từ tool MutPy cũ. Hệ quả: Chi phí chạy mutation vẫn cực kỳ cao. -> *Chưa giải quyết GAP.*
- **Paper 2 & 4 (DeepMutation/++):** Xây dựng bộ toán tử tĩnh cho mô hình DL và quét diện rộng không chọn lọc. Hệ quả: Sinh ra hàng ngàn mutant tương đương. -> *Chưa giải quyết GAP.*
- **Paper 3 (DeepCrime):** Đề xuất 35 toán tử làm thủ công. Áp dụng tĩnh lượng toán tử lớn như vậy khiến hệ thống quá tải thời gian. -> *Chưa giải quyết GAP.*
- **Paper 5 (Hassan 2023):** Dùng LLM sinh invariants cho phần cứng, nhưng không hề can thiệp vào quá trình sàng lọc hay tối ưu toán tử đầu vào (để cho tool Yosys tự làm). -> *Chưa giải quyết GAP.*
**=> Kết luận:** Tuyên bố GAP-T là hoàn toàn hợp lệ, chính xác và có cơ sở từ dữ liệu.

## Đánh giá khả thi (Feasibility Check)
| Tiêu chí | Trạng thái | Giải trình / Phương án kiểm soát |
|:---|:---|:---|
| **Dataset** | Xanh (An toàn) | Sử dụng lại tập Defects4J chuẩn hóa từ Paper 1. |
| **Tool/API** | Vàng (Rủi ro) | Cần quản lý API Key (GPT-4o) để không lố chi phí -> Sẽ giới hạn token và dùng prompt nén. |
| **Compute** | Xanh (An toàn) | Chạy thực nghiệm song song trên hạ tầng Google Colab đủ đáp ứng. |
| **Ground truth**| Xanh (An toàn) | Đối chứng trực tiếp kết quả với hệ thống baseline DeepMutation++. |
| **Skills** | Xanh (An toàn) | Team có kỹ năng Python, Software Engineering và Prompt Engineering. |
| **Thời gian** | Xanh (An toàn) | Khả thi code và chạy test trong tiến độ 7 tuần. |
| **Contribution**| Xanh (An toàn) | Đóng góp giá trị cao: Giải quyết trực tiếp bài toán chi phí của Mutation Testing. |

**=> Quyết định:** Với chỉ 1 rủi ro màu Vàng (đã có phương án mitigation), dự án được đánh giá ở mức **An toàn (Safe)** để tiếp tục thiết kế thực nghiệm.

## Kết luận (Conclusion) / Chốt GAP
Dựa vào phần Kiểm tra phản chứng (Falsification) và Đánh giá khả thi (Feasibility check) ở trên, nhóm quyết định chốt **[GAP-T]** làm GAP chính (Primary GAP) để tiến hành thiết kế thực nghiệm.

**Lý do lựa chọn và so sánh:**
* **Tại sao không chọn GAP-D (Dữ liệu):** Việc tự xây dựng lại hoặc gán nhãn thủ công (critical paths) cho toàn bộ tập dataset khổng lồ như Defects4J đòi hỏi khối lượng công việc cực kỳ lớn, tốn nhiều thời gian và rất dễ bị thiên kiến chủ quan (bias) của người dán nhãn.
* **Tại sao không chọn GAP-M (Metric):** Nếu chỉ đề xuất thêm một cặp Metric đánh giá (Trade-off) mà không xây dựng một công cụ/phương pháp mới để thực sự can thiệp và cải thiện metric đó, thì đóng góp (contribution) của nghiên cứu sẽ bị đánh giá là quá mỏng.
* **Tại sao không chọn GAP-S (Hạn chế chi phí):** GAP-S (tình trạng bùng nổ mutant dư thừa) thực chất chỉ là "triệu chứng" hay hệ quả. Trong khi đó, GAP-T (thiếu bộ lọc toán tử ngữ cảnh) mới là "nguyên nhân gốc rễ". Giải quyết được nguyên nhân gốc rễ (GAP-T) sẽ tự động triệt tiêu được hệ quả (GAP-S).
* **Lợi thế quyết định của GAP-T:** Việc dùng LLM làm bộ lọc (Context-aware Filter) đánh thẳng vào điểm yếu cốt lõi của các nghiên cứu trước (sự dư thừa). Dù có một rủi ro nhỏ về quản lý API, nhưng nhóm có sẵn nền tảng lập trình Python và kỹ năng Prompt Engineering. Hướng đi này vừa mang tính thời sự cao (Novelty tốt), có giá trị đóng góp rõ ràng (giảm chi phí), vừa đảm bảo tính khả thi cao để triển khai và demo thành công trong giới hạn 7 tuần.