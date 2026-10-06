# Official NSUT ChromaDB Knowledge Base

**Generated Date:** October 6, 2026  
**Project:** NSUT AI-Powered University Student Services Assistant  
**Database Path:** [`chroma_db/`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chroma_db/)  
**Build Script:** [`build_chromadb.py`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/build_chromadb.py)  

---

## 1. Overview & Specifications

- **Collection Name:** `nsut_official_knowledge`
- **Total Documents / Chunks Stored:** **83**
- **Distance Metric:** Cosine Similarity (`"hnsw:space": "cosine"`)
- **Embedding Model Used:** `all-MiniLM-L6-v2`
  - Engine: Built-in local ONNX embedding via `chromadb.utils.embedding_functions.DefaultEmbeddingFunction()`
  - Dimensions: **384**
  - Dependency: Fully local, zero external API keys required, fast CPU execution on macOS/Apple Silicon.
- **Database Location:** `./chroma_db` (persisted SQLite database + HNSW index)
- **Scope & Boundaries:** Contains **ONLY official NSUT university regulations, notices, rules, and administrative procedures**. No student records, personal data, or student-specific SQL schemas are stored.

---

## 2. Metadata Schema

Every vector document in `nsut_official_knowledge` contains the following 16 metadata fields for citation, provenance, and conflict awareness:

| Metadata Field | Type | Description |
|---|---|---|
| `doc_id` | String | Official document identifier (e.g., `NSUT-REG-2019`, `NSUT-20260915-ATT`) |
| `document_title` | String | Full title of the official university document |
| `document_type` | String | Type classification (`regulation`, `notification`, `guidelines`, `notice`, `addendum`) |
| `rule_id` | String | Canonical rule or procedure ID (e.g., `ATT-MIN-01`, `PROC-MAKEUP-APP`) |
| `category` | String | Domain category (Attendance, Fees, Summer Semester, Grading System, etc.) |
| `topic` | String | Specific topic or parameter of the rule |
| `page` | String | Source page number(s) |
| `section` | String | Source section title or Roman numeral |
| `clause` | String | Source clause or paragraph identifier (e.g., `Clause 11.2`, `Instruction A`) |
| `issue_date` | String | Official date of issuance (`YYYY-MM-DD` or `unknown`) |
| `effective_from` | String | Explicit effective start date or academic session (`unknown` if not explicit) |
| `effective_to` | String | Explicit expiration / cutoff date (`unknown` if ongoing) |
| `academic_year` | String | Applicable academic year (`2025-26`, `2026-27`, `2019-20`) |
| `applicability` | String | Target student cohort or programme applicability |
| `status` | String | Official status: `active` or `conflict` |
| `source_url` | String | Official university IMS/portal link (`unknown` if offline document) |

---

## 3. How to Load and Query the Persistent ChromaDB

Your teammates can load and query the database with standard Python code:

```python
import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize Persistent Client
client = chromadb.PersistentClient(path="chroma_db")

# 2. Use the matching embedding function
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

# 3. Load the collection
collection = client.get_collection(
    name="nsut_official_knowledge",
    embedding_function=embedding_fn
)

print(f"Loaded collection with {collection.count()} chunks.")

# 4. Perform a semantic similarity query
query_text = "What is the minimum attendance required to appear in exams?"
results = collection.query(
    query_texts=[query_text],
    n_results=3
)

# 5. Access retrieved chunks and citation metadata
for i in range(len(results["ids"][0])):
    chunk_id = results["ids"][0][i]
    document_text = results["documents"][0][i]
    metadata = results["metadatas"][0][i]
    distance = results["distances"][0][i]
    
    print(f"\nResult {i+1} [{chunk_id}] (Cosine distance: {distance:.4f}):")
    print(f"Document : {metadata['document_title']}")
    print(f"Citation : Page {metadata['page']}, Section {metadata['section']}, Clause {metadata['clause']}")
    print(f"Status   : {metadata['status']}")
    print(f"Text     : {document_text[:200]}...")
```

---

## 4. Re-running the Build (Idempotency)

The build script is deterministic and safe to re-run at any time:

```bash
python3 build_chromadb.py
```

It executes `collection.upsert()` using unique chunk IDs (`CHK-...`), ensuring existing records are safely refreshed without creating duplicates.

---

## 5. Source Documents & Provenance Summary

The database indexes **83 chunks** derived from **15 official NSUT documents**:

1. **Foundational Regulation (`NSUT-REG-2019`):** 48 chunks from the official *Regulations for Undergraduate Programme of Bachelor of Technology (2019-I(A))* covering degree requirements, grading (10-point scale), passing criteria, attendance statutes (Clause 11), branch change, evaluation scrutiny, and semester withdrawal.
2. **Attendance Notifications (`NSUT-20260915-ATT`, `NSUT-20260209-ATT`, `NSUT-20251030-ATT`):** 8 chunks covering daily portal verification, MSE condonation, 60% absolute floor, detention, CUMS lock deadlines, and medical certificate routing through HoD offices.
3. **Summer Semester & Backlogs (`NSUT-20260508-SUMMER`, `NSUT-20260127-BACKLOG`):** 8 chunks covering 5-course maximum, Study Mode vs. Exam-Only Mode, mandatory 75% attendance with zero relaxation, final-year 162-credit offering rule, and mandatory Study Mode for debarred/UFM/year-back students.
4. **Makeup Examinations (`NSUT-20260121-MAKEUP`):** 4 chunks covering summer makeup exams for students with 'I' grade due to illness or approved academic visits, 5-day post-illness deadline, and MESC scrutiny.
5. **Fee Schedules & Cutoffs (`NSUT-20260702-FEE2627`, `NSUT-20260702-FEEPAY`, `NSUT-20260721-DASA`):** 5 chunks covering multi-year cohort rates, DASA rates in INR, re-registration fees, late fine tiers, elective course priority cutoff (17.07.2026), and strict registration cutoff (14.08.2026).
6. **Hostel Administration (`NSUT-20251126-HOSTELFEE`, `NSUT-20260812-BH4FEE`, `NSUT-20260819-PROHIB`):** 6 chunks covering even semester hostel & mess rates, summer stay, check-in forfeiture with Rs. 2,000 deduction, non-refundable vacating policy, Ramanujan deadline, comprehensive prohibited items catalog, and quiet hours.
7. **Scholarships (`NSUT-20260811-CVSPK`):** 3 chunks covering CVSPK Death Of Earning Parent (DOEP) 100% full fee waiver running scheme, 90-day post-death deadline, and required application procedure.
8. **Academic Calendar (`NSUT-20260323-CAL`):** 1 chunk covering addendum dates for 8th sem project evaluation (15.05.2026) and practical examinations (19.05.2026).

---

## 6. Preserved Official Conflicts

Six chunks carry `status: "conflict"` representing genuine tensions between official university documents:
- **Summer Semester Fee:** Rs. 13,750/- per subject ([`CHK-NOT-FEE-20260702-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)) vs. Rs. 14,000/- Study Mode / Rs. 10,000/- Exam-Only Mode ([`CHK-NOT-SUM-20260508-02`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)).
- **Supplementary vs. Makeup Exams:** Ban on supplementary examinations ([`CHK-BACKLOG-NOSUPP-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)) vs. Summer Makeup examinations for 'I' grade ([`CHK-NOT-MAKE-20260121-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)).
- **MSE Attendance Condonation:** Notice stating no condonation at MSE ([`CHK-NOT-ATT-20260915-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)) vs. statutory Dean Academics 10% relaxation ([`CHK-ATT-RELAX-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)).
