---
name: answer-questions
description: Collect the open questions from every map, take the user's answers in one go, and apply what each answer changes (map nodes, gaps, after-MVP items, rules), then record the decisions in the panels. Use when the user answers open questions, makes product decisions about a flow, or asks what is still undecided.
---

# answer-questions

Maps raise questions: "code or password?", "keep the places found so far?". This skill turns answers into changes, so a decision never lives only in chat.

**Plugin root:** this skill's real directory, two levels up. Read `references/nodes-and-layout.md` (States of a gap, the decisions panel).
**Project:** `design/user-flow/`. If it's missing, run **init**.

## 1. Show what's open
- If the prompt has no answers yet, list `P.questions(state='open')` and `P.questions(state='waiting')`, grouped by map, numbered by id:
```
Journey 1 · Getting in
  Q1·3  Email sign-in: password, or a code sent to the email?
  Q1·1  (waiting on the developers) The 14 onboarding words for now…
```
- Ask the user to answer in any order: "Q1·3: code", "Q2·6: after MVP".
- If an answer needs research (for example "what do other apps do?"), do the research, give a recommendation, and wait. Mobbin is a good source for this kind of question.

## 2. Work out what each answer changes
For every answer, check each of these:
- **Gaps:** a gap's need changes (N1·2 becomes "code, not password"), a gap goes away (the answer makes it unnecessary), a gap becomes `later` (after MVP), or a new gap appears (the answer creates a new state). New gaps go through `P.add_gap`.
- **Map nodes:**
  - a decision loses or gains an exit
  - a card's note changes
  - a "needs design" card becomes a jump or exit pill (for example "Restart onboarding ↩ back to 1")
  - a label changes
- **Other questions:** one answer can settle another. Say so.
- **Rules:** a product or copy rule to add to `config.json` → `rules`, for example "Sharing is after MVP".
- **Someone else must confirm it:** record the answer with `owner`, for example `P.answer('Q1·1', text, date, owner='the developers')`. It stays amber until they do.

Show the list of changes and ask "apply?", unless the user said to go ahead.

## 3. Apply
- Record each answer with `P.answer(qid, decision, date[, owner])`. Write the decision as one plain sentence, for example "Continue works with nothing picked. Plans stay generic, like Skip."
- Edit the specs, gaps and rules as listed. Keep the layout rules: when a card becomes a pill, keep its column so the arrows still line up.
- Re-render every touched map. Run **sync-board** on each.

## 4. Report
- The decisions recorded.
- What changed on which map.
- New or removed gaps.
- What's still open.
