---
name: audit-flow
description: Audit a master map, journey map or flow map for missing screens and states (errors, empty, permissions, waiting, returning, undo) and add each one as a numbered needs-design gap. Use after drawing any map, or when the user asks what is missing, what edge cases were missed, or to check a map.
---

# audit-flow

Finds what's missing in a map and turns each finding into a gap with an id, so it can be explored later. This is where "needs design" comes from.

**Plugin root:** this skill's real directory, two levels up. Read `references/coverage-checklist.md` and `references/nodes-and-layout.md` (States of a gap).
**Project:** `design/user-flow/`. If it's missing, run **init**.

## 1. Pick the map
- Take it from the prompt (for example "journey 2", "the master map", "flow 1"). If there's no map, list what exists in `config.json` and ask.
- Read its spec, and screenshot its artboard so you audit what people actually see.

## 2. Audit
Go through the checklist line by line against the map:
- **Journey or flow:** at every screen and every decision, ask each checklist line. "Would the person see something here that isn't drawn?"
- **Master:** per area, check for missing empty, error and loading states; routes with no design; designs with no route; and areas with no way in.
- **Consistency:** check that
  - every decision has all its exits
  - every arrow is labelled
  - no gap duplicates another gap (search the registry by title and need)
  - `explored` gaps have their img
  - the counts on the board match the spec

## 3. Show findings before changing anything
One list, grouped by checklist line:
```
Failure · N2·11 (new) "Reading timed out": Argo gave up after 3 minutes. Say so, keep what it found, offer Try again. · where: row 1, after "Argo reads it"
Consistency · "Why not?" has no exit for offline. Add it.
```
Ask which to keep. Default is all.

## 4. Apply
- Add each kept gap: `P.add_gap(map_no, title, need, where)`. The id is assigned and never reused.
- Add it to the map spec with `m.gap(id, x, y, **P.g(gid))`, plus its arrows. Keep the layout rules: branch straight down, lane routing, spacing.
- Fix consistency issues in the spec.
- Re-render. Re-paste the map, or add just the new nodes if the layout didn't move. Screenshot and review.
- If the master map exists, add the new gaps to their areas.

## 5. Report
- New gap ids with their titles.
- Fixes made.
- The new counts.
- The gap you'd explore first, and why: on the persona's path, blocks the job, or high risk.
