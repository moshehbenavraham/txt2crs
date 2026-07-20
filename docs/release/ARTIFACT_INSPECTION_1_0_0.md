# `1.0.0` Live Artifact Inspection

**Status**: Complete
**Input class**: Synthetic, nonpersonal education topic
**Expected artifacts**: 16
**Reviewed artifacts**: 16

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
| Course | HTML | PASS | PASS | PASS | PASS | PASS | PASS | `052648cf9ff38a7dac4c366fbe21a769c9457d2888d6024df7de32dba0bb345e` | 6,508 |
| Course | Markdown | PASS | PASS | PASS | PASS | PASS | PASS | `7fdf5ca12dfc7f64e4b23aa388d284abcd7ba0a8eb443b78fb6fdc2211074d13` | 4,429 |
| Course | PDF | PASS | PASS | PASS | PASS | PASS | PASS | `e077ee4e70564b05757592a6b272dceb49661d0a179b5b48e1e023ae4303ecb7` | 17,230 |
| Course | DOCX | PASS | PASS | PASS | PASS | PASS | PASS | `278765fad5e2c387c866175971fe5bfbb582f2b4f7d55d01f091f7eb3a6bbedd` | 38,647 |
| Review pack | HTML | PASS | PASS | PASS | PASS | PASS | PASS | `bd67590a33e2a1919a5b1bb498933aff6c31f23506651764cb521f65bac1b39e` | 17,234 |
| Review pack | Markdown | PASS | PASS | PASS | PASS | PASS | PASS | `c4b44d6dac557fb42a4f8a07062191acf921361bb13b731bd5ee8ebd012fdf2f` | 15,464 |
| Review pack | PDF | PASS | PASS | PASS | PASS | PASS | PASS | `e087cead7f60dc3d846d5e96402aa639b406b7d1c0de051588fdecf09913e661` | 55,083 |
| Review pack | DOCX | PASS | PASS | PASS | PASS | PASS | PASS | `c3f4d21bbe1cf30d3b55f500b6848225b38ae58bf6b7b99db7b49707cc22b804` | 41,554 |
| Assessment | HTML | PASS | PASS | PASS | PASS | PASS | PASS | `15496e9786cbb7eb6324a639a03d439968803effd3651aede71ef6397ab4542c` | 3,182 |
| Assessment | Markdown | PASS | PASS | PASS | PASS | PASS | PASS | `ce34518dd613383d84fd564a967666a5fe0d11b820efdc3c16b64d84360abe0c` | 2,626 |
| Assessment | PDF | PASS | PASS | PASS | PASS | PASS | PASS | `8df2cfb2b5bd7c713820ef444e563e8175c5a535fc47d2a14612709e4b53863d` | 10,366 |
| Assessment | DOCX | PASS | PASS | PASS | PASS | PASS | PASS | `e67df27a075f282777274253ebc64c0bc04e562173537af12c52ef08fc8acfa9` | 37,756 |
| Answer key | HTML | PASS | PASS | PASS | PASS | PASS | PASS | `77073214fe3739056b871608b4eb267e500b29bb81d05f2eca66e5a5c76944c0` | 5,516 |
| Answer key | Markdown | PASS | PASS | PASS | PASS | PASS | PASS | `cf7974de9d8e04927e5abee19da07bf0bb0765427924c0a44d077cb7dcd0da0d` | 4,444 |
| Answer key | PDF | PASS | PASS | PASS | PASS | PASS | PASS | `43ea412d1b5608703c0f5ddc8eb81cd0e48aa1152154d7ed71842695b9b4aa7c` | 17,662 |
| Answer key | DOCX | PASS | PASS | PASS | PASS | PASS | PASS | `6fdb035853d64c096e5d3e94942fd6fffc54edfee5a22dd0464e2633842f9c95` | 38,175 |

## Cross-Publication Checks

- [x] Course objectives match the bounded synthetic request.
- [x] Review material covers the course without introducing an answer leak.
- [x] Student assessment instructions and items are complete.
- [x] Instructor answer key is separate and contains corresponding answers.
- [x] Sources are usable and unresolved conflicts are disclosed truthfully.
- [x] HTML, Markdown, PDF, and DOCX variants preserve the same publication
      meaning.
- [x] Owner-mismatch and missing-artifact reads remain indistinguishable.
- [x] Evidence contains no raw body or unrestricted private link.

The live run used exact `gpt-5.6-sol` through the dedicated ChatGPT
subscription runtime and real Tavily research. It completed in 258 seconds
with six sources, six excerpts, six model-usage records, nine durable
checkpoints, and exactly sixteen artifacts. The assessment intentionally omits
instructor evidence links; the separate answer key discloses the applicable
source links for every answer.

PDFs were opened, text-extracted, and visually reviewed page by page. DOCX
packages passed ZIP integrity checks and all four were converted successfully
through LibreOffice for rendered-layout inspection. Every format preserved the
same canonical course/review/question/answer content after normal
format-specific list and link presentation.

## Completion Rule

This file may be marked complete only after every `PENDING` becomes `PASS` or
a `FAIL` is resolved and the artifact is re-inspected. The canonical candidate
JSON validator independently requires the same sixteen unique pairs and six
passing dimensions.
