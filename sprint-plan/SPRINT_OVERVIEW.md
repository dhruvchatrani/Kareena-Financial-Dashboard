# Unibliss — Sprint Plan Overview

**Start Date:** Mon 2026-06-01  
**Sprint Cadence:** 2 weeks  
**Total Sprints:** 4  
**Total Tickets:** 19  

---

## Sprint 1: Critical Fixes & Quick Wins (Jun 1 – Jun 14)

| ID | Ticket | Priority | Est. Effort | Type |
|----|--------|----------|-------------|------|
| K-001 | Fix broken `Blended_Profit_Per_Unit` column reference | P0-Critical | 1 hr | Bug |
| K-002 | Remove unused imports across codebase | P3-Cleanup | 30 min | Chore |
| K-003 | Extract duplicated `clean_numeric()` to shared utility | P2-Important | 2 hr | Refactor |
| K-004 | Wire `audit_report.html` to a route | P3-NiceToHave | 2 hr | Feature |
| K-005 | Fix `FORMULA_DOCUMENTATION.md` silent placeholder | P3-NiceToHave | 1 hr | Bug |
| K-006 | Remove unused `static/` mount and empty `archive/` reference debt | P3-Cleanup | 30 min | Chore |

**Goal:** Stabilize the codebase, fix the crash bug, eliminate obvious code smells.

---

## Sprint 2: Architecture & Maintainability (Jun 15 – Jun 28)

| ID | Ticket | Priority | Est. Effort | Type |
|----|--------|----------|-------------|------|
| K-007 | Split `main.py` into modular route files | P2-Important | 8 hr | Refactor |
| K-008 | Set up Alembic for database migrations | P2-Important | 6 hr | Infrastructure |
| K-009 | Add consistent error handling and logging middleware | P2-Important | 6 hr | Improvement |
| K-010 | Wrap multi-file upload in a DB transaction | P2-Important | 4 hr | Improvement |

**Goal:** Improve maintainability so future work is safer and faster.

---

## Sprint 3: Security & Reliability (Jun 29 – Jul 12)

| ID | Ticket | Priority | Est. Effort | Type |
|----|--------|----------|-------------|------|
| K-011 | Add basic authentication layer | P1-MustHave | 10 hr | Security |
| K-012 | Add confirmation guard to `/admin/reset-db` | P1-MustHave | 3 hr | Security |
| K-013 | Add file upload validation (type, size, schema) | P1-MustHave | 5 hr | Reliability |
| K-014 | Improve `clean_numeric` error reporting (log on data loss) | P2-Important | 2 hr | Reliability |
| K-015 | Add CSV encoding fallback mechanism | P2-Important | 3 hr | Reliability |

**Goal:** Production-hardening — no data loss, no unauthorized access.

---

## Sprint 4: Performance & UX Polish (Jul 13 – Jul 26)

| ID | Ticket | Priority | Est. Effort | Type |
|----|--------|----------|-------------|------|
| K-016 | Optimize SKU-insights endpoint — cache / consolidate DB queries | P2-Important | 6 hr | Performance |
| K-017 | Add loading/processing state to upload flow | P3-NiceToHave | 4 hr | UX |
| K-018 | Make WhatsApp import directory configurable | P3-NiceToHave | 2 hr | UX |
| K-019 | Replace Pandas single-use groupby with `defaultdict` | P3-NiceToHave | 2 hr | Performance |

**Goal:** Faster page loads, better user experience.

---

## Effort Summary

| Sprint | Hours | Tickets |
|--------|-------|---------|
| Sprint 1 | ~7 hr | 6 |
| Sprint 2 | ~24 hr | 4 |
| Sprint 3 | ~23 hr | 5 |
| Sprint 4 | ~14 hr | 4 |
| **Total** | **~68 hr** | **19** |

---

## Prioritization Legend

| Priority | Meaning |
|----------|---------|
| P0-Critical | Causes incorrect data or crashes — fix immediately |
| P1-MustHave | Blocks production use |
| P2-Important | Significant improvement to code health or reliability |
| P3-NiceToHave | Polish, cleanup, or nice-to-have |
