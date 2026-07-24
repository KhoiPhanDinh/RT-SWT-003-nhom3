# Search Log — Mutation Testing Enhancement with AI
**Thành viên:** Nguyễn Trường Vinh
**Ngày thực hiện:** 2026-06-01

---

## Chuỗi tìm kiếm (Query Strings)

### String A
**Query nguyên văn:**
```
("mutation testing" OR "mutant generation" OR "mutant selection") AND ("artificial intelligence" OR "AI-guided" OR "large language model" OR "LLM") AND ("Java" OR "Java projects")
```
**Database:** ACM Digital Library
**Bộ lọc:** Latest
**Ngày search:** 2026-06-01 00:49
**Số kết quả (paper):** 302

---

### String B
**Query nguyên văn:**
```
"mutation testing" AND ("mutant selection" OR "mutant reduction") AND ("random sampling" OR "random selection" OR "random mutant generation" OR baseline)
```
**Database:** ACM Digital Library
**Bộ lọc:** Latest
**Ngày search:** 2026-06-01 00:33
**Số kết quả (paper):** 58

---

### String C
**Query nguyên văn:**
```
"mutation testing" AND ("AI" OR "LLM") AND ("testing effort" OR "effort reduction" OR "cost reduction" OR "execution time") AND "Java"
```
**Database:** ACM Digital Library
**Bộ lọc:** Latest
**Ngày search:** 2026-06-01 00:56
**Số kết quả (paper):** 153

---

## Tổng hợp trước dedup

| Database | String | Kết quả (paper) |
|---|---|---|
| ACM Digital Library | String A | 302
| ACM Digital Library | String B | 58
| ACM Digital Library | String C | 153
| **Tổng trước dedup** |  | **238** |
| **Sau dedup** |  | **207** |
| Số bị loại (trùng lặp) |  | 21 |
  