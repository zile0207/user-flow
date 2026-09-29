# Coverage checklist (audit-flow)

Walk a map against every line. Anything missing becomes a gap (`P.add_gap(...)`) with a need of 1 or 2 sentences that say what the screen must show, not how it should look.

1. **Ways in:** each tab, the create button, notifications, deep links, sharing from another app, the home or top area, search.
2. **Decisions:** every user choice (including Back, Cancel, Skip, Later, Undo) and every system check (signed in, first time, found, allowed, online). Every decision has all its exits drawn.
3. **Permissions:** allowed, denied, asked later in context, and denied for good (the app must say how to fix it in Settings).
4. **Waiting:** loading, background work, the user leaving mid-way, notified when it's done (and when notifications are off).
5. **Failure:** no signal, a timeout, private or deleted content, invalid input, a duplicate, partial results.
6. **Empty and first time:** nothing yet; the first use compared with the tenth.
7. **Returning:** a new phone, a reinstall, quitting half-way (resume or restart).
8. **Undo and removal:** what gets undone, what goes with it, and confirmation for anything destructive.
9. **Account and data:** signed out mid-flow, session expired, the account deleted elsewhere.
10. **After MVP:** keep it with `later` so the MVP versions of neighbouring screens drop the entry point.

For each finding, record:
- **gap id and title:** the title is the screen's job ("Couldn't sign you in")
- **need:** what the screen must show
- **where:** the map, row, and which node it hangs off
- **why:** the checklist line it came from

Report the new gaps as a list, then add them to the map spec with `m.gap(..., **P.g(gid))` and wire their arrows.

**Before any finding becomes a gap:** look for it in the library (`_uf.py find <words>`, then a screenshot). If the screen exists, it goes on the map as a card with that frame (or the gap becomes `found`), not as a gap.
