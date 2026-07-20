# `1.0.0` Live Artifact Inspection

**Status**: Pending live GPT-5.6 plus Tavily course
**Input class**: Synthetic, nonpersonal education topic
**Expected artifacts**: 16
**Reviewed artifacts**: 0

This ledger records bounded judgments for the one representative live job.
The reviewer inspects each private artifact locally. The tracked ledger stores
no artifact body, prompt, provider payload, account identifier, local path, or
private download link.

## Review Scale

- `PASS`: The inspected artifact satisfies the dimension.
- `FAIL`: A concrete release-blocking problem exists.
- `PENDING`: The real artifact has not yet been inspected.

Each row must pass:

- alignment with its deliverable purpose and synthetic learning goal;
- usable citations or appropriate source disclosure;
- readable format-specific rendering;
- hash, byte-count, and private-delivery integrity;
- owner-private access behavior; and
- student assessment versus instructor answer separation.

## Inspection Ledger

| Deliverable | Format | Alignment | Citations | Formatting | Integrity | Private access | Answer separation | SHA-256 | Bytes |
|-------------|--------|-----------|-----------|------------|-----------|----------------|-------------------|---------|-------|
| Course | HTML | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Course | Markdown | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Course | PDF | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Course | DOCX | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Review pack | HTML | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Review pack | Markdown | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Review pack | PDF | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Review pack | DOCX | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Assessment | HTML | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Assessment | Markdown | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Assessment | PDF | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Assessment | DOCX | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Answer key | HTML | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Answer key | Markdown | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Answer key | PDF | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |
| Answer key | DOCX | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Pending | Pending |

## Cross-Publication Checks

- [ ] Course objectives match the bounded synthetic request.
- [ ] Review material covers the course without introducing an answer leak.
- [ ] Student assessment instructions and items are complete.
- [ ] Instructor answer key is separate and contains corresponding answers.
- [ ] Sources are usable and unresolved conflicts are disclosed truthfully.
- [ ] HTML, Markdown, PDF, and DOCX variants preserve the same publication
      meaning.
- [ ] Owner-mismatch and missing-artifact reads remain indistinguishable.
- [ ] Evidence contains no raw body or unrestricted private link.

## Completion Rule

This file may be marked complete only after every `PENDING` becomes `PASS` or
a `FAIL` is resolved and the artifact is re-inspected. The canonical candidate
JSON validator independently requires the same sixteen unique pairs and six
passing dimensions.
