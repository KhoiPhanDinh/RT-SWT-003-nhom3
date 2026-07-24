# PRISMA Flowchart

**Search Results Date:** 31/05/2026

## Database Searching Records

| Search String | Database | Records |
|---|---|---:|
| String A | Google Scholar | 202 |
| String B | Google Scholar | 52 |
| String C | Google Scholar | 71 |
| **Total before deduplication** |  | **325** |

## PRISMA Flow

```text
┌──────────────────────────────────────────────┐
│ Records from database searching              │
│ (N = 325)                                    │
└──────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│ Records after duplicate removal              │
│ (N = 249)                                    │
└──────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐        ┌──────────────────────────────┐
│ Vòng 1: Title + Abstract Screening           │───────▶│ Excluded (N = 228)   
|	                                         |	        |Reason: IC1 = 3 ; IC4 = 11; IC5=1|  						|				
│ Screened records (N = 249)                   │        │ Reason: EC4 = 206 ; EC2 = 7          │
└──────────────────────────────────────────────┘        └──────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐        ┌──────────────────────────────┐
│ Vòng 2: Full-text Screening                  │───────▶│ Excluded (N = 11)            │
│ Full-text assessed (N = 21)                  │        │ Reasons: IC 4 = 11  │
└──────────────────────────────────────────────┘        └──────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│ Included in Evidence Table                   │
│ (N = 10)                                      │
└──────────────────────────────────────────────┘
```

