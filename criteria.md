# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False positives on my writing

In each of three trials, submit the same 10 different pieces I wrote myself, including at least two written in a plain style. At most one of the 10 may receive the `ai` guess in each trial.

**Why this target:** A false accusation can harm a writer's trust and reputation, so I want a low tolerance for it, including for people who write simply. Ten pieces are a small sample, so meeting this target would not establish a real-world false-positive rate.

---

## 2. Score separation

Before running the evaluation, select 10 known AI-generated pieces and 10 different pieces I wrote myself. In each of three trials, the mean `confidence` score for the AI set must be at least 0.15 higher than the mean for the human set. Use the same pieces in each trial.

**Why this target:** The score should show a meaningful difference between the two groups, while allowing individual pieces to overlap. This measures separation on the chosen examples, not accuracy on all writing.

---

## 3. All three labels are reachable

Select a fixed set of no more than 30 valid pieces before the evaluation. In each of three trials, submissions from that set must produce all three guesses: `human`, `unsure`, and `ai`. Each response's label must match the exact text and score range documented in the README.

**Why this target:** A label that only exists in the mapping but cannot be reached by actual submissions does not give readers the intended range of outcomes. Checking the response text and range also catches mismatches between the contract and the implementation.

---

## 4. Appeals are recorded and put under review

In each of three trials, submit five valid pieces and appeal each returned content ID with a distinct non-empty reason. All five appeals must return HTTP 200 and `under_review`; the audit log must retain each original decision and contain a later appeal entry with the matching content ID, exact reason, and `under_review` status.

**Why this target:** A writer needs a reliable way to challenge a decision, and reviewers need both the original decision and the writer's explanation. Five separate appeals test that the link works for more than one item.

---

## 5. Invalid submission input is rejected

In each of three trials, send these five JSON objects to `/submit`, each with a valid `creator_id`: one missing `text`, one with `text` set to an empty string, one with whitespace only, one with `text` set to `null`, and one with a 10,001-character text string. All five must return HTTP 400 with `error` equal to `invalid_input`, and none may create a decision entry in the audit log.

**Why this target:** Rejecting malformed or oversized input makes the endpoint predictable and prevents invalid material from being treated as a completed decision. The length case checks the boundary specified in the endpoint contract.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
