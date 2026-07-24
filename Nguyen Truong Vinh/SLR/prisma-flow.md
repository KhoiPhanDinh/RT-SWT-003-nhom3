# PRISMA Flow — Mutation Testing Enhancement with AI

```
[Records từ database searching (N = 228)]   <-- Tổng từ search-log.md
        |
[Sau khi xóa duplicate (N = 207)]   <-- = số dòng trong 01_all_records.csv  (EC1 = 21)
        |
+--------------------------------------------------+
| Vòng 1 — Screened title + abstract (N = 207)  |
|   --> Excluded (N = 184): EC4=182, IC2=1, EC3=1        |
+--------------------------------------------------+
        |
23 paper pass  <-- = (INCLUDE + UNSURE) trong 02_after_screening_v1.csv
        |
+--------------------------------------------------+
| Vòng 2 — Full-text assessed (N = 23)        |
|   --> Excluded (N = 13): EC4=12, IC5=1           |
+--------------------------------------------------+
        |
[Final included (N = 10)]  <-- = số dòng trong 03_final_included.csv
```
