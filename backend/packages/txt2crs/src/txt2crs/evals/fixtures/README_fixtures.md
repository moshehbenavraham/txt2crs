# Built-in Evaluation Fixtures

These small private inputs exercise every category declared by
`EvaluationCase`: ordinary prompts, long transcripts, malformed input, noisy
OCR/extraction, conflicting evidence, prompt injection, inaccessible sources,
RTL content, high-risk topics, quota exhaustion, cancellation, invalid schemas,
and citation failure.

`built_in_evaluation_cases()` computes a SHA-256 hash from each exact packaged
file, so unreviewed fixture drift is visible to the replay system.
