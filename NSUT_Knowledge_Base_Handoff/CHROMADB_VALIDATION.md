# ChromaDB Validation Report

**Generated Date:** October 6, 2026  
**Project:** NSUT AI-Powered University Student Services Assistant  
**Database Path:** [`chroma_db/`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chroma_db/)  
**Collection Name:** `nsut_official_knowledge`  

---

## 1. Validation Results Summary

- **Chunk Count:** **83**
- **Reload Test:** **PASS** (Persistent collection opened from disk without re-processing)
- **5 Query Results:** **PASS** (All 5 queries returned relevant official university rules/procedures)
- **Provenance Metadata:** **PASS** (100% of retrieved results contain document title, page, section, clause, and URL)
- **Student-Data Check:** **PASS** (Zero student-specific SQL records, marks, attendance logs, or personal profiles present)
- **Any Errors:** **None**

---

## 2. Test Queries & Retrieved Results Detail

### 1. Query: `"attendance requirement"`
- **Status:** **PASS**
- **Top Result:** [`CHK-ATT-MIN-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)
- **Document Title:** *Regulations for Undergraduate Programme of Bachelor of Technology (Regulations 2019-I(A)), NSUT*
- **Category / Topic:** Attendance | Minimum attendance to be eligible to appear in MSE/ESE for a subject
- **Provenance:** Page 18, Section 11 ATTENDANCE AND DETENTION, Clause 11.2
- **Rule Status:** `active`

### 2. Query: `"supplementary examination"`
- **Status:** **PASS**
- **Top Result:** [`CHK-BACKLOG-NOSUPP-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)
- **Document Title:** *Regulations for Undergraduate Programme of Bachelor of Technology (Regulations 2019-I(A)), NSUT*
- **Category / Topic:** Supplementary & Makeup Examinations | Regulations state there are no supplementary examinations
- **Provenance:** Page 19, Section 12 PROMOTION AND PASSING A COURSE, Clause 12.3
- **Rule Status:** `conflict` (Official ban on supplementary exams preserved alongside Summer Makeup opportunities)

### 3. Query: `"fee rules"`
- **Status:** **PASS**
- **Top Result:** [`CHK-NOT-FEE-20260702-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)
- **Document Title:** *Annual fee structure for all programs (2022-23 admitted batch) across 5 years, No.F. 220(287)Annual Fee/2017/Acad/NSUT/995, dated 02/07/2026*
- **Category / Topic:** Fees | Re-Registration Fees for Regular Semesters, Summer Semester, and MOOCs Policy
- **Provenance:** Page 17, Section Re-Registration, Clause Items (i) to (iv)
- **Rule Status:** `conflict`

### 4. Query: `"scholarship rules"`
- **Status:** **PASS**
- **Top Result:** [`CHK-PROC-CVSPK-DOEP`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)
- **Document Title:** *Notice - Applications invited under CVSPK for D.O.E.P scholarship (Death Of Earning Parent) with DOEP application form, F. No. 84(344)/2026-27/DSW/NSUT/, dated 11/08/2026*
- **Category / Topic:** Scholarships | Procedure for Applying for CVSPK Death Of Earning Parent (DOEP) 100% Fee Waiver
- **Provenance:** Page 1-2, Section INSTRUCTIONS & NOTICE, Clause Section A & Instructions A-D
- **Rule Status:** `active`

### 5. Query: `"examination eligibility"`
- **Status:** **PASS**
- **Top Result:** [`CHK-ATT-MIN-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl) / [`CHK-ADM-MIN-MARKS-01`](file:///Users/adityayadav/Desktop/NSUT%20PROJECT/chunks.jsonl)
- **Document Title:** *Regulations for Undergraduate Programme of Bachelor of Technology (Regulations 2019-I(A)), NSUT*
- **Category / Topic:** Attendance | Minimum attendance to be eligible to appear in MSE/ESE for a subject
- **Provenance:** Page 18, Section 11 ATTENDANCE AND DETENTION, Clause 11.2
- **Rule Status:** `active`

---

## 3. Scope & Privacy Verification

- **Student Database Status:** Completely untouched. No tables, records, marks, or attendance data modified or stored.
- **RAG Pipeline Status:** Existing codebase unmodified.
- **Data Integrity:** All chunks are strictly derived from verified official university publications.

---

# CHROMADB READY FOR HANDOFF
