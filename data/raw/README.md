# data/raw/

**NOTE (chưa đầy đủ):** thư mục này để chứa dữ liệu gốc theo cấu trúc RBL-4 §"File mới thêm vào
repo sau RBL-4", nhưng nhóm hiện **không lưu lại bản PIT XML report gốc** (mutations.xml) trong repo —
các report này được sinh ra và đọc trực tiếp trên Kaggle (ephemeral disk, ~70GB, không persist giữa các
session) rồi tổng hợp ngay thành `data/full_ground_truth.csv`. Cột `source_xml` trong
`data/full_ground_truth.csv` vẫn giữ nguyên đường dẫn Kaggle gốc (ví dụ
`/kaggle/working/results_full20/pit_reports/Lang_7f/pit-reports/mutations.xml`) để truy vết, nhưng file đó
không còn tồn tại để tải lại.

## Nguồn dữ liệu

- **Benchmark:** Defects4J — <https://github.com/rjust/defects4j>
- **Projects:** Commons Lang (`Lang`), Commons Math (`Math`)
- **Versions đã chạy:** xem cột `version` trong `data/full_ground_truth.csv` (Lang: 1f,3f,4f,6f,7f,8f,9f,10f;
  Math: 1f–10f).
- **Mutation testing tool:** PIT (Pitest) — <https://pitest.org>
- **Ngày tải/chạy PIT:** NOTE — chưa ghi lại chính xác ngày chạy từng batch; xem `logs/pilot_pit_log.txt`
  (RT-SWT-003-nhom3/logs) cho log gần nhất có timestamp.

## Cấu trúc cột (data/full_ground_truth.csv)

`detected, status, numberOfTestsRun, sourceFile, mutatedClass, mutatedMethod, methodDescription,
lineNumber, mutator, indexes, blocks, killingTest, description, project, version, target_mode,
source_xml, local_index, killed, mutant_id`

- `killed`: True/False, ground truth dùng để tính mutation score.
- `mutant_id`: khóa nối với `data/full_sample.csv` (mutant pool + code context) và với
  `results/full_gpt_selected.csv` / `results/full_random_selected.csv`.

## Known scope imbalance (threat to validity — xem notes.md)

PIT được chạy ở **scope khác nhau** giữa hai project:

- Lang: batch rộng (`target_mode=full`, `source_xml` trỏ tới `results_full20`), ~147 class/version.
- Math: chỉ ~1 class/version dù đã chạy tới 10 version (1f–10f) → chỉ ra đúng 18 group
  (project,version,class_name).

Đây là lý do Math chỉ có 18 paired unit trong khi Lang có 739 (xem `notes.md` mục "Threat to validity
chưa xử lý").
