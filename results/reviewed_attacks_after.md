# Reviewed attacks: after

Evasion: BROKE means a successful response without an AI flag (including unsure). False positive: BROKE means an AI accusation. Junk strings: BROKE means a decision was made instead of refusal. Arabic is legitimate writing; a confident AI accusation is treated as the failure, not acceptance of its script. Prompt injection: check fixed response labels and audit integrity. Flood: accept within budget and reject above it.

Totals: {'BROKE': 13, 'HELD': 43}

| ID | Status | Guess | Combined | Verdict | Stage and mechanism |
|---|---|---|---|---|---|
| EV01 | 200 | unsure | 0.2553 | BROKE | signal one / combining rule: Typos lower model score to 0.1635 while style stays at 0.6226; the 0.8 model weight pulls the result to 0.2553. |
| EV02 | 200 | unsure | 0.534 | BROKE | signal two / combining rule: Broken-up sentences lower the style score to 0.2927; the weighted score stays inside the unsure band. |
| EV03 | 200 | unsure | 0.63 | BROKE | signal two / combining rule: The pasted quotation changes surface counts; both reported signals remain below the AI-label cutoff. |
| EV04 | 200 | unsure | 0.6116 | BROKE | signal one: Unusual words increase perplexity; predictability is not a reliable authorship test, so the score stays below the AI cutoff. |
| EV05 | 200 | unsure | 0.3331 | BROKE | both signals: Heavy editing lowers both signals, and their weighted mean remains unsure. |
| EV06 | 200 | unsure | 0.5269 | BROKE | signal two: Unequal sentence lengths lower the variation component; the result does not cross the AI-label threshold. |
| EV07 | 200 | unsure | 0.5672 | BROKE | signal two: Added punctuation lowers the punctuation component without establishing a different author; the combined result is unsure. |
| EV08 | 200 | unsure | 0.3008 | BROKE | signal one / route: The short input still contains enough tokens to pass validation; its score of 0.3008 is unsure, not an AI flag. |
| EV09 | 200 | unsure | 0.6592 | BROKE | both signals / combining rule: The added opening alters both predictability and surface statistics; the combined result is below the AI cutoff. |
| EV10 | 200 | ai | 0.9273 | HELD | label mapping: The attempted evasion still received the AI label or was rejected. |
| FP01 | 200 | unsure | 0.5991 | HELD | label mapping: A human-writing attack breaks the check only if it receives the AI label. |
| FP02 | 200 | unsure | 0.7177 | HELD | label mapping: A human-writing attack breaks the check only if it receives the AI label. |
| FP03 | 200 | unsure | 0.7619 | HELD | label mapping: A human-writing attack breaks the check only if it receives the AI label. |
| FP04 | 200 | unsure | 0.7733 | HELD | label mapping: A human-writing attack breaks the check only if it receives the AI label. |
| FP05 | 200 | unsure | 0.7682 | HELD | label mapping: A human-writing attack breaks the check only if it receives the AI label. |
| FP06 | 200 | unsure | 0.8037 | HELD | label mapping: A human-writing attack breaks the check only if it receives the AI label. |
| FP07 | 200 | unsure | 0.7967 | HELD | label mapping: A human-writing attack breaks the check only if it receives the AI label. |
| FP08 | 200 | unsure | 0.3208 | HELD | label mapping: A human-writing attack breaks the check only if it receives the AI label. |
| PI01 | 200 | unsure | 0.4457 | HELD | route / label mapping: The input remained data: a normal score, a fixed label, and one unmodified-schema decision entry were recorded. |
| PI02 | 200 | unsure | 0.2343 | HELD | route / label mapping: The input remained data: a normal score, a fixed label, and one unmodified-schema decision entry were recorded. |
| PI03 | 200 | unsure | 0.5846 | HELD | route / label mapping: The input remained data: a normal score, a fixed label, and one unmodified-schema decision entry were recorded. |
| PI04 | 200 | unsure | 0.5046 | HELD | route / label mapping: The input remained data: a normal score, a fixed label, and one unmodified-schema decision entry were recorded. |
| PI05 | 200 | unsure | 0.5996 | HELD | route / label mapping: The input remained data: a normal score, a fixed label, and one unmodified-schema decision entry were recorded. |
| PI06 | 200 | unsure | 0.5529 | HELD | route / label mapping: The input remained data: a normal score, a fixed label, and one unmodified-schema decision entry were recorded. |
| MF01 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| MF02 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| MF03 | 200 | human | 0.1 | BROKE | route: The string passes the length/token checks despite controls or non-prose content; a provenance decision is made without a suitable writing sample. |
| MF04 | 200 | human | 0.149 | BROKE | route: The string passes the length/token checks despite controls or non-prose content; a provenance decision is made without a suitable writing sample. |
| MF05 | 200 | ai | 0.8981 | BROKE | route: The string passes the length/token checks despite controls or non-prose content; a provenance decision is made without a suitable writing sample. |
| MF06 | 200 | ai | 0.9575 | BROKE | route: The string passes the length/token checks despite controls or non-prose content; a provenance decision is made without a suitable writing sample. |
| MF07 | 200 | unsure | 0.8804 | HELD | label mapping: Valid Arabic text is accepted without a confident AI accusation; language support is still unvalidated. |
| MF08 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ01 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ02 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ03 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ04 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ05 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ06 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ07 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ08 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ09 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ10 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ11 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| RQ12 | 400 | - | None | HELD | route: The malformed input should be rejected with HTTP 400. |
| FL01_01 | 200 | human | 0.1139 | HELD | route: Request 1: expected HTTP 200 within this fresh-process minute budget. |
| FL01_02 | 200 | human | 0.1139 | HELD | route: Request 2: expected HTTP 200 within this fresh-process minute budget. |
| FL01_03 | 200 | human | 0.1139 | HELD | route: Request 3: expected HTTP 200 within this fresh-process minute budget. |
| FL01_04 | 200 | human | 0.1139 | HELD | route: Request 4: expected HTTP 200 within this fresh-process minute budget. |
| FL01_05 | 200 | human | 0.1139 | HELD | route: Request 5: expected HTTP 200 within this fresh-process minute budget. |
| FL01_06 | 200 | human | 0.1139 | HELD | route: Request 6: expected HTTP 200 within this fresh-process minute budget. |
| FL01_07 | 200 | human | 0.1139 | HELD | route: Request 7: expected HTTP 200 within this fresh-process minute budget. |
| FL01_08 | 200 | human | 0.1139 | HELD | route: Request 8: expected HTTP 200 within this fresh-process minute budget. |
| FL01_09 | 200 | human | 0.1139 | HELD | route: Request 9: expected HTTP 200 within this fresh-process minute budget. |
| FL01_10 | 200 | human | 0.1139 | HELD | route: Request 10: expected HTTP 200 within this fresh-process minute budget. |
| FL01_11 | 429 | - | None | HELD | route: Request 11: expected HTTP 429 within this fresh-process minute budget. |
| FL01_12 | 429 | - | None | HELD | route: Request 12: expected HTTP 429 within this fresh-process minute budget. |
