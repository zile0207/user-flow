---
name: map-flow
description: Map one job to be done end to end, from the moment the need appears to the job being done, across whatever areas it touches. Use when the user wants a user flow, a JTBD flow, an end-to-end task, or asks how someone gets from a goal to done.
---

# map-flow

A flow map is one job, start to done. It's thinner than a journey:
- Row 1 is the job's main path, and it crosses areas freely.
- Extra rows hold only the branches that change whether the job gets done.
- Screens come from any journey. Gaps come from the registry, and new ones go into the registry too.

**Plugin root:** this skill's real directory, two levels up. Read `references/nodes-and-layout.md` (Three levels, Flow maps) and `references/project-and-paper.md`.
**Project:** `design/user-flow/`. If it's missing, run **init**.

## 1. The job
Write it in the JTBD form and confirm it with the user:
> When **<situation>**, I want to **<motivation>**, so I can **<outcome>**.

Example: "When I have a free Saturday, I want to turn the videos I saved into a plan, so I can go out without deciding everything myself."

Also agree on the flow's number (the next free `no` in `maps.flows`), plus:
- **Start:** the trigger, as a start pill with the persona and moment.
- **Done:** the outcome, as an exit pill, "Job done: …".

## 2. Trace it
- Walk the persona's path through the source screens and existing journey specs: the shortest real path from start to done.
- At each step, ask: can the job fail or stall here? If yes, add a decision. Its exits are the branch that recovers, or a jump into the journey that covers it ("→ 2 · Collecting, row 3").
- Reuse journey screens: same img, same ref. Don't redraw a journey's detail here. Link to it with exit or jump pills.
- Run `references/coverage-checklist.md` on this path only. Missing steps become gaps in the registry under the journey that owns the area.

## 3. Spec, render, paste
- Write `specs/f<no>.py` with `Map(<no>, P.img_dir)`.
  - The number is only used for the header; gap ids come from the registry.
  - Row 1: start pill → screens, decisions, background work → the "Job done" exit pill.
  - Row 2 and down: recovery branches only.
  - Keep it tight. A flow that needs more than 3 rows is a journey. Say so and offer **map-journey**.
- Render, then create the artboard `F<no> · <short job> · flow` to the right of the journeys. Paste, screenshot and review.
- Record it in `config.json` → `maps.flows` with the job sentence.

## 4. Report
- The job sentence.
- Steps from start to done, and taps on the happy path.
- Where it can fail, and the gaps.
- Next: **audit-flow** for a deeper pass, or **explore-design** on a gap that blocks the job.
