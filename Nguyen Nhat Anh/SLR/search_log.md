**Thành viên:** Nguyễn Nhật Anh
**Ngày thực hiện:** 2026-06-01

---

## Chuỗi tìm kiếm (Query Strings)

### String A
**Query nguyên văn:**
```
mutation testing llm
```
**Database:** Semantic Scholar  
**Bộ lọc:** Year 2018–2026  
**Ngày search:** 2026-06-01  
**Số kết quả:** 20 papers  

---

### String B
**Query nguyên văn:**
```
mutation testing
```
**Database:** Semantic Scholar  
**Bộ lọc:** Year 2018–2026  
**Ngày search:** 2026-06-01  
**Số kết quả:** 11 papers  

---

### String C
**Query nguyên văn:**
```
AI mutation testing
```
**Database:** Semantic Scholar  
**Bộ lọc:** Year 2018–2026  
**Ngày search:** 2026-06-01  
**Số kết quả:** 9 papers  

---

## Tổng hợp trước dedup

| Database | String | Kết quả |
|---------|--------|---------|
| Semantic Scholar | String A | 20 |
| Semantic Scholar | String B | 11 |
| Semantic Scholar | String C | 9 |
| **Tổng trước dedup** | | **40** |
| **Sau dedup** | | **38** |
| Số bị loại (trùng lặp) | | 2 |

---

## Ghi chú
- Thực hiện dedup bằng: Excel (chức năng Remove Duplicates theo tiêu đề bài báo).
- Có 2 bài báo bị trùng lặp chéo giữa các string tìm kiếm. Dữ liệu thực tế quét được đưa vào vòng PRISMA là 38 bài riêng biệt.

---

### Tóm tắt tiến độ thực tế (PICO topic)
**SV 01:** Nguyễn Nhật Anh
- Các String A, B, C tìm kiếm trên Semantic Scholar -> 40 kết quả.
- Sau dedup: 38 papers -> file `01_all_records.csv` có 38 dòng (loại 2 dòng trùng).
- Screening V1: 11 bị loại -> 27 pass -> file `02_V1_screening.csv` ghi nhận 11 EXCLUDE + 27 INCLUDE.
- Full-text V2: 22 bị loại -> 5 final -> file `03_final_included.xlsx` chốt hạ 5 INCLUDE.
