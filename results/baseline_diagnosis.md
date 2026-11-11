# Baseline diagnosis and improvement decision

Baseline service: model weight 0.8, style weight 0.2, human cutoff 0.15,
AI cutoff 0.85. The detector, signals, labels, and acceptance targets are unchanged.

- All 56 staff rows were attempted: 42 HELD, 14 BROKE under the explicit rules
  in `reviewed_attacks_before.md`. Nine evasion rows avoided an AI flag; four
  non-prose/control inputs received decisions; MF07 received an unsupported
  high-confidence AI accusation on Arabic writing. Each broken ID has a stage
  and mechanism in the reviewed results.
- The eight staff false-positive examples all received unsure. That is a
  successful avoidance of accusations on these examples, not proof of human origin.
- Criterion 1: original authorship prerequisite unverified. Supplemental fixture
  measurements were 0/10 AI flags in all three trials. No human false-positive
  rate is established.
- Criterion 2: original authorship prerequisite unverified. The fixture score gap
  was 0.23268 in all trials (reference mean 0.39535; comparison mean 0.62803).
- Criteria 3, 4, and 5: MET in all three trials, with three labels reached,
  five linked appeals recorded, and five invalid submissions refused respectively.

## Single improvement selected before the after runs

Raise only AI_THRESHOLD from 0.85 to 0.8896. The historical human reference L02
scored 0.8895, higher than every staff false-positive example. Because the supplied
reference fixtures do not establish personal authorship, use this identified
historical reference and the staff false-positive family as the confirmed-human
calibration pool. This is an explicit substitution of the calibration source,
not a claim that the personal-writing criteria were evaluated.

The chosen cutoff is one four-decimal increment above the largest score in that
pool. It should move both L02 and MF07 out of the AI band, without changing their
signal or combined scores. This is tuning to observed examples, not validation on
unseen writing. Raising the cutoff can let more AI text avoid an AI flag. It is
also expected to remove the only AI-labeled input from the frozen coverage set,
so criterion 3 may regress. Keep the set fixed and report that regression.

No input-validation, signal, model, weight, human-cutoff, or label-wording change
is part of this improvement. The route's junk-input weaknesses remain for future work.
