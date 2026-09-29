---

id: BLK-TOOLBOX-PDF-READING-V1
name: PDF Reading Toolbox
type: toolbox
scope: mixed
version: 1.0
status: active
revised: 2026-04-23
summary: Default workflow for efficient local-first reading of large PDF documents by agents.
---------------------------------------------------------------------------------------------

# PDF Reading Toolbox

This document defines the default workflow for working with PDF files, especially
**large PDFs** such as standards, building codes, manuals, long reports, and
technical references.

The goal is to make PDF work:

* local-first
* section-targeted
* token-efficient
* resumable
* traceable across sessions

Agents must avoid treating a PDF as a blob to send wholesale to an LLM provider
when a more selective workflow is possible.

---

## Core Principle

**Do not send a full PDF to an LLM unless there is a strong reason to do so.**

A PDF should first be treated as a structured local artifact that can be:

* inspected
* searched
* split
* indexed
* summarized progressively

LLM usage should happen **after narrowing the scope** to the relevant pages or
sections whenever possible.

---

## Primary Working Artifact

When a PDF has already been read in whole or in part, the agent must create and
maintain a companion notes file:

```
reading_notes_<short_pdf_name>.md
```

Examples:

```
reading_notes_asce7_wind.md
reading_notes_nbcc_load_combinations.md
reading_notes_vendor_manual_x.md
```

This file becomes the **primary reference artifact** for future work once the
document or relevant sections have already been processed.

Agents should prefer reusing this notes file over re-reading or re-sending the
same PDF content repeatedly.

---

## Purpose of the Reading Notes File

The reading notes file exists to:

* preserve what has already been read
* reduce repeated LLM costs
* reduce repeated local parsing work
* provide a durable summary for future sessions
* track where specific answers came from

It is not a polished report. It is a working artifact for humans and agents.

---

## Recommended Reading Notes Structure

```md
# Reading Notes — <document title>

## Metadata
- Source file:
- Short name:
- Date created:
- Last updated:
- Total pages:
- Status: not started | in progress | partial | substantial | complete

## Document Structure
- Part ...
- Chapter ...
- Section ...
- Appendix ...

## Reading Progress
- Pages reviewed:
- Sections reviewed:
- Remaining high-value sections:

## Key Findings
- ...
- ...

## Section Notes
### Section <x>
- pages:
- topic:
- summary:
- key definitions:
- key rules:
- open questions:

## Extracted References
- term:
- location:
- note:

## Outstanding Questions
- ...

## Next Useful Cuts
- pages ...
- section ...
- appendix ...
```

---

## Default Workflow for Large PDFs

### Step 1 — Inspect Structure First

Before attempting full analysis, inspect the document structure.

Priority order:

1. table of contents
2. bookmarks / outline
3. headings visible from extracted text
4. index
5. appendices
6. glossary / definitions section

Do **not** start by blindly parsing the full PDF if a structure-first pass can
identify the relevant section.

---

### Step 2 — Define the Real Query

Translate the request into a narrow retrieval target.

Examples:

* “load combinations” → specific section, not whole code
* “roof snow exceptions” → snow chapter + exceptions
* “warranty exclusions” → warranty section only
* “torque values” → installation appendix

---

### Step 3 — Search Locally First

Use local tools to:

* extract text
* search keywords
* identify candidate pages

Do this before invoking an LLM.

---

### Step 4 — Split to Relevant Section(s)

Extract the smallest useful chunk:

* a chapter
* a section
* a table with context
* a 10–30 page cut instead of a 900-page PDF

---

### Step 5 — Analyze the Cut

Use LLMs only on:

* isolated sections
* extracted text
* relevant context

---

### Step 6 — Write Back to Notes

Update `reading_notes_<short_name>.md` with:

* pages reviewed
* section summary
* key rules
* uncertainties
* next sections to explore

---

## Local-First Tooling Rule

* Use local tools first
* Prefer Python + `uv` when options are equivalent
* Otherwise use the most efficient tool available

---

## Tool Selection Guidance

### Local tools for:

* extraction
* search
* splitting
* indexing

### LLM for:

* interpretation
* synthesis
* answering scoped questions

---

## Practical Heuristics

* Structure before depth
* Notes before re-read
* Smallest useful cut
* Expand search terms
* Record uncertainty
* Preserve traceability

---

## When Full PDF Is Acceptable

Only when:

* document is small
* no usable structure exists
* task requires full context
* narrowing failed

---

## Anti-Patterns

Avoid:

* sending full PDFs by default
* re-reading processed sections
* vague answers without traceability
* relying on LLM memory instead of notes

---

## Minimal Example Workflow

**Task:** Find load combinations in a building code

1. inspect TOC
2. search locally
3. isolate section
4. extract pages
5. analyze section
6. write notes
7. reuse notes later

---

## Status

Authoritative v1
