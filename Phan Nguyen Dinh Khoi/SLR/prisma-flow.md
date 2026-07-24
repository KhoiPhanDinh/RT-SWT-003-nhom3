# PRISMA Flow — Mutation Testing Enhancement with AI (SE1903)

[Records từ database searching (N = 67)]   <- Tổng từ search-log.md (A=25, B=17, C=25)
        |
        v
[Sau khi xóa duplicate (N = 63)]           <- = số dòng trong 01_all_records.csv (6 bản trùng bị loại)
        |
        v  Vòng 1: Title + Abstract Screening
+-------------------------------------------------+
| Screened title+abstract (N = 63)                | --> Excluded (N = 53)
|                                                 |     IC2 = 24  (xuất bản trước 2018)
|                                                 |     EC4 = 21  (ngoài phạm vi: MT-of-DL, test-gen, FL, ...)
|                                                 |     EC3 = 2   (poster / extended abstract: id 9, 34)
|                                                 |     IC5 = 1   (review không có thực nghiệm: id 3)
+-------------------------------------------------+
        |
        v  Vòng 2: Full-text Screening
+-------------------------------------------------+
| Full-text assessed (N = 8)                     | --> Excluded (N = 6)
|                                                 |     EC1 = 1 (Trùng lặp nội dung file)
|                                                 |     EC4 = 1 (Dùng công thức toán học, không dùng AI).
+-------------------------------------------------+     EC2 = 4 (Không truy cập đc full text)
        |                                               
        v
[Included trong Evidence Table (N = 8)]   <- = số dòng v2_decision = Include trong 03_final_included.csv
