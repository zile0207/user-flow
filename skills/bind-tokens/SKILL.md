---
name: bind-tokens
description: Bind library screens to the project's design tokens, one journey (or a list of frames) at a time, so every colour, font size, line height, weight, tracking, radius and space is a var(--token), SVG strokes and fills included. Use when the user asks to tag, bind, tokenise or apply variables to screens, a journey, a board or the library, when a new token is added, or to check which screens still use literal values.
---

# bind-tokens

Screens use the project's design tokens, never literal values. This skill binds the literals that are already on the canvas: it reads each frame, works out every change on the computer, and writes them in a few large `update_styles` calls.

**Plugin root:** this skill's real directory, two levels up. The binder is `lib/uf/tokens.py`, run through `specs/_uf.py`.
**Project:** `design/user-flow/`. The token file is `config.json` → `sources.paper.tokens.source` (Paper's `create_tokens` form, plus the optional `snap` and `keep` tables). Every Paper file of the project must already hold these tokens: `get_tokens` shows the same content hash as `sources.paper.tokens.content_hash`.

## Where the tags go
- **Bind the library frames** (`sources.paper.library_file_id`), not only the copies on a board. Boards show copies made from the library frame's JSX; a copy keeps whatever the frame had when it was copied. A tag added only to a copy is lost the next time the copy is refreshed, and a tag on the frame reaches every copy made after it.
- **Work one journey at a time.** The batch is the library frames one board shows (10 to 50 frames), or frames the user names. A batch is 1 to 4 write calls.
- **Before a board is painted,** bind its frames first: the copies then arrive tagged, at no extra cost. **If the board is already painted,** refresh its copies afterwards (step 6).

## Pace
- One writer per Paper file, and one call at a time: parallel calls have stalled the Paper server and lost work.
- Batch inside each call. One `update_styles` call takes every layer that gets the same change, across every frame in the batch (thousands of node ids are fine). Never write one call per layer or per screen.
- Don't use `find_nodes` to read frames: it stops at 200 results and can't see SVG colours. The binder reads `get_tree_summary` (node ids) and `get_jsx` (styles), which are smaller and complete.

## Steps
1. **Which frames:** render the board's spec, then `python3 design/user-flow/specs/_uf.py bind-status <board>`. It lists the board's library frames that aren't bound yet.
2. **Read them,** one call at a time, for each frame:
   - `get_tree_summary(fileId <library>, nodeId <frame>, depth 30)`
   - `get_jsx(fileId <library>, nodeId <frame>, format "inline-styles")`

   Then store them without retyping: `_uf.py bind-from-transcript <this session's .jsonl>` (Claude Code: the newest `.jsonl` in `~/.claude/projects/<this repo>/`). Elsewhere, save each result to a file and run `_uf.py bind-read <frame> <tree file> <jsx file>`. The harness's saved-result files work as they are.
3. **Plan:** `_uf.py bind-plan <board> --board <board>` (or `_uf.py bind-plan <name> <frame…>`). It prints:
   - the layers and values to bind;
   - the calls, as files `out/bind/<batch>/NN.json` of about 20 KB each;
   - **values with no token.** Don't guess these. Show the user the table (kind, value, how many layers, example ids). For each value they choose one of three:
     - add a token: to the token file first, then to every Paper file, then to the app's theme;
     - snap it to an existing token: add it to `snap`;
     - leave it literal on purpose: add it to `keep`.

     Then plan again.
   - **parts that didn't line up** (the tree and the JSX differ in shape). These are skipped, never guessed. Read the frame again. `get_tree_summary` stops at depth 10, so for a deeper part, read that part as its own frame (`bind-read <part>`) and add its id to the plan.
4. **Write:** for each file, in order: `update_styles(fileId <library>, updates = <the file's JSON exactly as it is>)`. Wait for each call before the next. If a call returns `ignoredStyles`, note them for the report.
5. **Check:**
   - If the same values come back after the write (Paper took the call but kept the literal; seen on some sheets' `paddingInline`), try once more with the longhands; if they still stay, record them: `_uf.py bind-refused <prop> <node…>`. Plans then skip them, and the report lists them.
   - Read each frame again with `get_jsx` only (update_styles doesn't change the tree), run `bind-from-transcript`, and plan again. Frames with nothing left to bind are recorded as bound in `design/user-flow/bound.json`.
   - Screenshot two of the frames at scale 1. Tokens resolve to the values that were there, so nothing should move. A snap changes a value by a pixel or two.
6. **Check the copies on a painted board:** read each card with `get_jsx(fileId <board file>, nodeId <card>)`, run `bind-from-transcript`, then `_uf.py bind-check <board file id> <card node…>`. It walks the copied screen inside each card (not the card's own label) and lists every value that should be a token. "all copies tagged" means done.
7. **Refresh painted copies** (only if a board already shows these frames):
   - Boards that inline library frames: `bind-from-transcript` has already put the tagged JSX in the frame cache. Run `_uf.py stale <board> <frame…>`, then **sync-board**.
   - Boards that clone a Frames page: remake those copies (`references/project-and-paper.md` → Frames page), then `stale` and sync.
   - Boards with placed screens: `_uf.py stale <board> <frame…>`, sync (the cards get empty slots), then stage and place those screens again (`sync.md` → Placed screens).
8. **Report:**
   - the frames bound (`bind-status`);
   - the values left literal and why (the keep list, or the user's choice);
   - any parts that were skipped;
   - the boards to refresh.

## What the binder does
- **Exact value first:** a value that equals a token binds to that token.
- **Then the snap table:** near-duplicates the user approved.
- **Colours with alpha:** `#FFFFFF38` becomes `color-mix(in oklab, var(--color-white) 22%, transparent)`, Tailwind's opacity modifier. This needs the solid colour to be a token.
- **Pills:** a radius of at least half the layer's shorter side becomes the pill token (the 999px radius).
- **Line heights:** a line height equal to its font size's default becomes that default (`var(--text-sm-line-height)`). Any other line height becomes a leading token.
- **Font faces:** "Switzer-Bold"-style face names become the family token plus the weight token.
- **Margins** bind only on an exact match. Negative and odd margins are layout offsets.
- **Never tokens:** images, gradients, shadows, positions, widths and heights, and anything in `keep`.
- **Already bound** values (`var(`, `color-mix(`) are left alone, so planning a frame twice is safe.

## New screens
Explorations and promoted screens are written with `var(--token)` from the start: the project's `ui_kit.py` uses tokens, never hex values. After promote-design, run `bind-plan` on the promoted frames. It should show nothing to bind; if it shows anything, bind it before the promote step is reported done.

## Subagents
Ask the user before handing any of this to a subagent. If they allow it, use **one** subagent for the writes (a file has one writer), with this prompt:
> You are applying pre-computed style updates to a Paper file. Do exactly this and nothing else.
> First load the tool: call ToolSearch with query "select:mcp__paper__update_styles" (max_results 1).
> For each file, in this order: <absolute paths>
> 1. Read the file.
> 2. Call mcp__paper__update_styles with fileId "<library file id>" and updates set to the file's JSON exactly as it is. Wait for the result before the next file.
> Do not call any other Paper tool. If a call fails, retry it once; if it fails again, stop and report the file and the error.
> Reply with one line per file: the file name, "ok" or the error, and any ignoredStyles.
