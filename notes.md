# notes.md — RT-SWT-003-nhom3-Tuan8 (RBL-4, Tuần 8 Full Experiment)

Folder này gộp lại tất cả deliverable của **Tuần 7 (Pilot)** và **Tuần 8 (Full Experiment)** theo đúng
cấu trúc yêu cầu trong `RBL-4/` ("File mới thêm vào repo sau RBL-4"), lấy từ hai nơi đang làm việc:

- `RT-SWT-003-nhom3/` — repo gốc của nhóm (Tuần 7 pilot, config `selection_scope: global`, còn bug đã biết).
- `LR_v2/LR/` — pipeline đã sửa bug cho full experiment (Tuần 8, config `selection_scope: by_group`).

Đây là **hợp nhất + đối chiếu**, không phải chạy lại từ đầu — mọi số liệu trong `results/summary.csv` và
`figures/` được tính trực tiếp từ dữ liệu thật đã có (`data/full_sample.csv`, `data/full_ground_truth.csv`,
`results/full_gpt_selected.csv`, `results/full_random_selected.csv`), không có số liệu giả định.

---

## 1. Hai bug đã phát hiện và sửa (trước khi tổng hợp folder này)

### Bug 1 — `selection_scope: global` khiến Math bị chọn 0 mutant

Khi chọn top-10% GPT theo **toàn bộ pool** (`global`), điểm `usefulness_score` thô của GPT4o-mini chỉ có
5 mức (1–5) nên bị trùng (tie) rất nhiều ở mức điểm cao nhất. Tie-break theo `mutant_id` tăng dần khiến
`"Lang_..."` luôn thắng `"Math_..."` (thứ tự alphabet), và vì số mutant Lang bị tie ở điểm cao nhất đã vượt
quá ngân sách top-10%, **Math bị chọn 0 mutant**. Bằng chứng bug này được giữ lại tại
`results/plots_by_group_evidence/full_gpt_selected_global_BUGGY_DO_NOT_USE.csv` (Lang=5070, Math=0) và
`results/plots_by_group_evidence/full_random_selected_global_BUGGY_DO_NOT_USE.csv` — **không dùng hai file
này để tính metric**, chỉ giữ làm bằng chứng cho phần Threats to Validity.

**Sửa:** đổi `config.yaml` → `selection_scope: by_group`, `group_columns: [project, version, class_name]`,
viết `scripts/reselect_by_group.py` để chọn top-10% **trong từng group** thay vì toàn bộ pool.

### Bug 2 — group theo (project, version) thay vì (project, version, class_name)

Một bản dẫn xuất trung gian (`full_gpt_selected_by_group.csv` / `full_random_selected_by_group.csv`,
đã xoá, không có trong folder này) được sinh bởi một script group theo `["project","version"]` (gộp theo
version, không theo class), khiến 6/18 group nhỏ của Math vẫn bị chọn 0 mutant GPT dù đã áp dụng
`by_group`. Đã xác nhận và sửa: `results/full_gpt_selected.csv` / `results/full_random_selected.csv` hiện
tại group đúng theo `project + version + class_name` (đủ 757/757 group có mutant được chọn ở cả hai
nhánh — xem `results/paired_mutation_scores.csv`).

### Bug 3 — `random_baseline.py` không thực sự reproducible dù `seed=42` cố định (phát hiện 2026-07-08,
trong lúc dọn file trùng ở folder này)

`random_select_by_group()` (trong `scripts/random_baseline.py`) tính seed riêng cho từng group bằng
`hash((seed, str(group_key))) % (2**32)`. Hàm `hash()` built-in của Python **salt ngẫu nhiên theo từng
process** cho kiểu `str` (`PYTHONHASHSEED` randomization, mặc định từ Python 3.3) — nên dù `random_seed: 42`
cố định trong `config.yaml`, mỗi lần chạy lại `random_baseline.py`/`reselect_by_group.py` ở một process mới
sẽ ra **một `full_random_selected.csv` khác nhau**. Phát hiện được vì chạy `reselect_by_group.py` hai lần
liên tiếp cho hai kết quả Wilcoxon khác nhau (pooled r_rb: 0.399 → 0.365 → ...).

Đây là vi phạm trực tiếp lời hứa reproducibility ở proposal §5.5 ("Random seed... 42 for reproducibility"),
§7.1 Threat 2 và §7.4 Threat 2 ("Random seed chính là 42 để reproducibility").

**Sửa:** thay `hash()` bằng `hashlib.sha256` (thuật toán cố định, không phụ thuộc process) trong hàm mới
`stable_group_seed()`. Đã verify: chạy `reselect_by_group.py` 3 lần ở 3 process Python riêng biệt cho ra
`full_random_selected.csv` giống hệt nhau (cùng md5). **Số liệu trong `results/summary.csv` và
`results/full_analysis.ipynb` ở mục 3 dưới đây là số liệu SAU KHI sửa Bug 3** (đã confirm reproducible).

⚠️ Bug này cũng tồn tại y hệt trong `LR_v2/LR/scripts/random_baseline.py` (code gốc, chưa sửa) — nếu còn
dùng pipeline ở đó để chạy thêm (vd. cho amendment Math), cần áp dụng cùng fix trước khi chạy.

---

## 2. Deviation so với proposal §7.1 (đã ghi nhận, không phải lỗi kỹ thuật cần amendment)

Proposal §7.1 mô tả pilot là "chọn ngẫu nhiên 10–20% N" và lưu thành `pilot_sample.csv` +
`pilot_ground_truth.csv` riêng. Trên thực tế, nhóm **không tách một subsample 10–20% riêng** — do PIT vốn
đã chạy theo từng batch (class/version) trải dài từ Tuần 7 sang Tuần 8, "pilot" trong thực tế là chạy GPT
ranking trên **toàn bộ mutant pool đang có tại thời điểm đó** (`results/pilot_llm_output.csv`, 50,694
mutant = bằng đúng `data/full_sample.csv`), rồi Tuần 8 chỉ scale thêm phần selection (`by_group`) và phân
tích thống kê, không chạy GPT ranking lại từ đầu.

→ Vì vậy folder này **không có** `data/pilot_sample.csv` / `data/pilot_ground_truth.csv` riêng biệt như cây
thư mục mẫu trong RBL-4 — dùng chung `data/full_sample.csv` + `data/full_ground_truth.csv` cho cả hai giai
đoạn. Đây là một deviation đã biết, ghi nhận công khai ở đây thay vì tạo file giả để khớp tên.

---

## 3. Kết quả RQ1 (Tuần 8) — xem `results/summary.csv`, `results/full_analysis.ipynb`

| Subset | n_group | p-value (Wilcoxon, một phía) | r_rb (rank-biserial) | mean MS_GPT | mean MS_random | Kết luận |
|---|---:|---:|---:|---:|---:|---|
| Pooled (Lang+Math) | 757 | 1.73e-09 | 0.425 | 0.834 | 0.779 | Case 1 — ủng hộ H1, **nhưng Lang chiếm 739/757 = 97.6%**, không nên diễn giải là đại diện "cả hai project" |
| Lang | 739 | 1.63e-09 | 0.436 | 0.834 | 0.778 | Case 1 — ủng hộ H1 rõ ràng, độc lập |
| Math | 18 (11 cặp non-zero) | 0.344 | 0.136 | 0.834 | 0.831 | Case 3 — xu hướng tích cực (GPT nhỉnh hơn random, win 7 vs 4) nhưng chưa đủ ý nghĩa thống kê/effect size |

*(Số liệu trên là sau khi sửa Bug 3 — xem mục 1. Trước khi sửa, do bug non-reproducible, một lần chạy đã
từng cho Math ra Case 4 (p=0.50, r_rb=0.00, mean MS_GPT < mean MS_random) — số đó KHÔNG dùng nữa vì không
reproducible.)*

Ngưỡng theo proposal: `p < 0.05` **và** `r_rb ≥ 0.30` (medium effect, Cohen 1988; ngưỡng lấy từ Jimenez et
al. 2018). Sub-group rule (proposal §6.3, pre-registered): chỉ chạy test riêng nếu `n_group ≥ 10` — cả Lang
(739) và Math (18) đều ≥ 10 nên **cả hai đều được chạy test chính thức** (không phải trường hợp "n quá nhỏ
nên chỉ báo cáo descriptive").

**Kết luận trung thực:** RQ1 được ủng hộ (H1) khi tính chung hoặc chỉ tính trên Commons Lang. Trên Commons
Math, có xu hướng tích cực nhưng **chưa đủ bằng chứng thống kê** để kết luận H1 (Case 3, không phải Case 4)
— đây là finding hợp lệ theo §6.4 của proposal (không viết "GPT4o-mini vô dụng", chỉ viết "chưa đủ bằng
chứng trên Math dưới budget đã đánh giá").

---

## 4. Threat to validity CHƯA xử lý — so sánh Lang vs Math (generalization)

`data/raw/README.md` đã ghi: PIT chạy Math ở scope hẹp (~1 class/version) trong khi Lang chạy ở scope rộng
(~147 class/version), xác nhận qua cột `source_xml` trong `data/full_ground_truth.csv` — không phải suy
đoán. Hệ quả: 18 group của Math là **toàn bộ** những gì pipeline hiện có, không phải một mẫu con đại diện.

→ Kết quả riêng lẻ Lang-vs-Math (so `MS_GPT4o` với `MS_random` trong cùng project) **vẫn dùng được**, vì cả
hai nhánh GPT/Random đều lấy từ cùng pool Math. Nhưng **so sánh chéo** (dùng kết quả Math để nói "GPT4o-mini
generalize kém hơn trên Math so với Lang", hoặc dùng làm RQ3/generalization claim) **chưa nên dùng** cho tới
khi Math được chạy lại ở scope rộng tương đương Lang — đang chờ **amendment** (chốt số version Math sẽ chạy
lại, giống quy trình đã chạy cho Lang, trước khi rerun trên Kaggle).

---

## 5. HARKing compliance (proposal §6.5)

- Metric (Mutation Score), statistical test (Wilcoxon signed-rank, một phía), threshold (`p<0.05` và
  `r_rb≥0.30`), và sub-group rule (`n_group≥10`) đều lấy nguyên văn từ `team-synthesis/proposal.md` §5.6/§6.1/
  §6.3, **không đổi sau khi thấy kết quả**.
- Kết quả Math yếu hơn kỳ vọng **không** dẫn tới đổi test, đổi threshold, hay bỏ Math ra khỏi báo cáo — được
  báo cáo nguyên trạng ở mục 3 và 4 phía trên.

---

## 6. File map (nguồn gốc từng file trong folder này)

| File | Nguồn | Vai trò |
|---|---|---|
| `data/full_sample.csv`, `data/full_ground_truth.csv` | `LR_v2/LR/data/` (giống hệt `RT-SWT-003-nhom3/data/`, đã diff = 0) | Mutant pool + ground truth killed/survived |
| `results/pilot_llm_output.csv`, `pilot_api_log.txt`, `pilot_cost_log.csv`, `pilot_validation_report.txt`, `pilot_gpt_checkpoint.jsonl` | `RT-SWT-003-nhom3/results/` | Deliverable Tuần 7, snapshot đóng băng (không sửa lại) |
| `results/full_llm_output.csv`, `full_api_log.txt`, `full_cost_log.csv`, `full_validation_report.txt`, `full_gpt_checkpoint.jsonl` | Bản sao của `pilot_*` tương ứng ở trên | `config.yaml` (`gpt_ranking_output`/`api_log_file`/`cost_log_file`/`validation_log_file`/`checkpoint_file`) trỏ vào các file `full_` này — đây mới là path pipeline Tuần 8 thực sự ghi ra khi chạy `run_experiment.py`. Nội dung hiện **giống hệt** bản `pilot_` vì Tuần 8 không cần gọi lại API (GPT ranking đã cover toàn bộ pool từ Tuần 7, xem deviation mục 2) — đây là sự thật của project, không phải file rác, nên giữ cả hai tên theo đúng cây thư mục RBL-4 yêu cầu |
| `results/pilot_gpt_selected.csv`, `pilot_random_selected.csv`, `pilot_analysis.ipynb` | `RT-SWT-003-nhom3/results/` | Deliverable Tuần 7 thật sự riêng biệt (số liệu khác bản `full_`, xem deviation ở mục 2) |
| `results/full_gpt_selected.csv`, `full_random_selected.csv` | `LR_v2/LR/results/` (bản đã sửa Bug 1+2, `by_group`) + Bug 3 đã sửa | Input chính cho `compute_metric.py` — nội dung khác thật với bản `pilot_*` (5438 vs 5070 dòng) |
| `results/plots_by_group_evidence/` | `LR_v2/LR/results/*_global.csv` + `plots/` | Bằng chứng Bug 1 (giữ cho Threats to Validity), KHÔNG dùng để tính metric |
| `results/summary.csv`, `results/paired_mutation_scores.csv`, `results/full_analysis.ipynb` | Mới tạo Tuần 8 | Phân tích thống kê chính thức RQ1 |
| `figures/fig1_distribution.png`, `fig2_comparison.png` | Mới tạo Tuần 8 (từ `full_analysis.ipynb`) | Boxplot phân phối + so sánh theo project |
| `scripts/*.py` | `LR_v2/LR/scripts/` (đã sửa Bug 3 trong `random_baseline.py`) + `compute_metric.py`, `test_api.py`, `run_experiment.py` mới | Pipeline đầy đủ (validate → rank → random → reselect → metric) |

### Đối chiếu pilot_ vs full_ trong results/ (2026-07-08)

Đã đối chiếu byte-level + nội dung từng cặp `pilot_*` / `full_*` trong `results/`:

| Cặp file | Kết quả đối chiếu | Quyết định |
|---|---|---|
| `pilot_llm_output.csv` vs `full_llm_output.csv` | Cùng 50,694 dòng, cùng `usefulness_score` mọi mutant_id, chỉ khác cột `rank` (thứ tự tie-break hiển thị) | **Giữ cả hai** — cây thư mục RBL-4 liệt kê rõ cả hai là deliverable riêng (T7 và T8 ★); `config.yaml` trỏ pipeline output vào `full_llm_output.csv` |
| `pilot_api_log.txt` vs `full_api_log.txt` | Giống hệt byte-for-byte | **Giữ cả hai** (cùng lý do — cả hai đều được liệt kê trong cây thư mục yêu cầu) |
| `pilot_cost_log.csv` / `pilot_validation_report.txt` / `pilot_gpt_checkpoint.jsonl` vs bản `full_` tương ứng | Giống hệt byte-for-byte (md5 trùng) | Giữ cả hai để nhất quán với `config.yaml`, dù không nằm trong minimal tree bắt buộc |
| `pilot_gpt_selected.csv` vs `full_gpt_selected.csv` | **Khác nhau thật** (5070 vs 5438 dòng — bản `full_` đã sửa Bug 1/2) | Giữ cả hai (khác nội dung thật) |
| `pilot_random_selected.csv` vs `full_random_selected.csv` | **Khác nhau thật** | Giữ cả hai |
| `pilot_analysis.ipynb` vs `full_analysis.ipynb` | **Khác nhau thật** (notebook pilot mô tả cơ bản, notebook full có Wilcoxon/effect size) | Giữ cả hai |

*(Ghi chú lịch sử: ban đầu đã thử xoá 4 file `full_llm_output.csv`/`full_api_log.txt`/`full_cost_log.csv`/
`full_validation_report.txt` vì trùng nội dung với `pilot_*`, và trỏ `config.yaml` về `pilot_*`. Sau khi đối
chiếu lại với cây thư mục RBL-4 chính thức (yêu cầu cả `pilot_llm_output.csv` VÀ `full_llm_output.csv ★`
tồn tại riêng), đã khôi phục cả 5 file `full_*` và trả `config.yaml` về trỏ `full_*` như ban đầu. Việc thử
xoá rồi khôi phục lại này chính là lúc phát hiện ra Bug 3 ở mục 1 — mỗi lần đổi `config.yaml` đều chạy lại
`reselect_by_group.py` + `compute_metric.py` để verify pipeline không gãy.)*

---

## 7. Bước tiếp theo (chưa làm trong folder này)

Xem **`amendment_v1.0_to_v1.1.md`** — amendment đầy đủ (đúng template proposal §8.6) cho việc chạy lại PIT
trên Math ở scope rộng hơn, kèm kế hoạch thực hiện 8 bước chi tiết (chốt 5 version trước khi chạy, rerun
PIT trên Kaggle, cập nhật dataset, GPT ranking chỉ cho mutant mới, random baseline, reselect_by_group,
tính lại metric, báo cáo trung thực). Cần GV duyệt amendment trước khi thực hiện.

Sau khi hoàn thành: rerun `scripts/run_experiment.py` → `scripts/compute_metric.py` → cập nhật
`results/summary.csv`, `results/full_analysis.ipynb`, `figures/`, rồi commit lên GitHub theo checklist
RBL-4 (không commit `.env`, API key, `__pycache__/`).
