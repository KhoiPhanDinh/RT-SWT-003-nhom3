# Search Log — PICO
**Thành viên:** Trần Trúc Vỹ

**Ngày thực hiện:** 2026/06/01

---

## Chuỗi tìm kiếm (Query Strings)

### String A
---
("mutation testing" OR "mutant generation" OR "mutant selection") AND ("artificial intelligence" OR "AI-guided" OR "large language model" OR "LLM")
---
**Database:** OpenAlex

**Bộ lọc:** Year 2018–2026

**Ngày search:** 2026-01-06 9:13 pm

**Số kết quả:** 139 papers

### String B
---
("mutation testing") AND ( "mutant selection" OR "mutant reduction") AND ("random sampling" OR "random selection" OR "random mutant generation" OR baseline)
---
**Database:** OpenAlex

**Bộ lọc:** Year 2018–2026

**Ngày search:** 2026-01-06 9:14 pm

**Số kết quả:** 0 papers

### String C
---
("mutation testing") AND ("AI" OR "LLM") AND ("testing effort" OR "effort reduction" OR "cost reduction" OR "execution time") AND ("Java")
---
**Database:** OpenAlex

**Bộ lọc:** Year 2018–2026

**Ngày search:** 2026-01-06 9:15 pm

**Số kết quả:** 1 paper

---
## Tổng hợp trước dedup

| Database | String | Kết quả |
|---------|--------|---------|
| OpenAlex | String A | 139 |
| OpenAlex | String B | 0 |
| OpenAlex | String C | 1 |
| **Tổng trước dedup** | | **140** |
| **Sau dedup** | | **102** |
| Số bị loại (trùng lặp) | | 38 |
---
## Ghi chú
- Thực hiện dedup bằng: [OpenAlex / tay / Excel]
- Paper trùng nhau nhiều nhất: các paper trên arXiv (Cornell University) xuất hiện cả ở ArXiv.org
```
---
### Phễu PRISMA của bài này (khớp với CSV)
- String A: `("mutation testing" OR "mutant generation" OR "mutant selection") AND ("artificial intelligence" OR "AI-guided" OR "large language model" OR "LLM")` → OpenAlex = 139 kết quả
- Tổng trước dedup: 140 (String A 139 + String B 0 + String C 1)
- Sau dedup: 102 papers → file 01_all_records.csv có 102 dòng
- Screening V1: 83 bị loại → 19 pass → file 02 có cột v1_decision = 83 EXCLUDE + 19 INCLUDE/UNSURE
- Full-text V2: 14 bị loại → 5 final → file 03 có cột v2_decision = 5 INCLUDE
---