---
name: init
description: Set up user-flow in a project. Connects the design sources (Paper, Figma, codebase), records the persona and brand colour, builds the app's UI kit from its confirmed screens, and creates design/user-flow/.
disable-model-invocation: true
---

# init

Creates `design/user-flow/` in the current repo, so every other user-flow skill knows where the screens are and how the app looks.

**Plugin root:** this skill's real directory (follow symlinks), then two levels up. Read `references/project-and-paper.md` first. `templates/project/` holds the starter files.

## 1. Ask (one message, skip anything the prompt already answered)
- **Where the designs live:** a Paper file link, a Figma file link, and/or "the codebase only". For Paper and Figma, which page has the finished screens.
- **Where boards go:** a page for maps (offer "User Journey"), and a page for explorations (offer "Exploration"). Both are in the same file as the confirmed screens. If they don't exist yet, offer to create them (`create_page`).
- **The library:** the page that holds every confirmed screen of the app, however messy (`library_page`). Journeys place these screens in context, and nothing becomes a needs-design gap while the library has it. Confirmed explorations are promoted there too (`promote_page`), unless the user names another page.
- **Legacy files:** any older file to mark as legacy (`legacy_file_ids`), so no skill writes to it.
- **A readme per file:** offer an `agents.md` page in each Paper file with one readme frame: what the file and its pages are for, how the project's files connect, the rules for agents, and the product. Record each in `config.json` → `sources.paper.files` (`file_id`, `name`, `readme`: page and frame, `pages`). Every skill reads them once per session.
- **The rules:** the app's copy rules (vocabulary, banned words, what never to guess) and product rules (what may be asked, when). Read them from AGENTS.md, CLAUDE.md, a spec or a story page if they exist. Draft them, and confirm with the user.
- **The persona:** a name and a line about them. Offer to draft it from a story or spec page if one exists.
- **The router,** if there's a codebase: Expo Router, Next.js app router, React Navigation, or other. Detect it first, then confirm.

## 2. Read the sources
- **Paper:** get_basic_info for the screens page. List the artboards (the chapters) and the screens inside each, with their node ids. Screen IDs come from the page's own naming (chapter·step) where it has one.
- **Figma:** the Figma MCP. List the frames on the screens page, with their node ids.
- **Codebase:** walk the routes folder. Each route is a screen; `ref` is the route path.

- **The library:** index it (`references/project-and-paper.md` → The library): `get_tree_summary(root_node_<library page>, depth 1)` → `out/library_tree.txt` → `_uf.py library out/library_tree.txt`.

Never export screen images. Boards show real frames (live copies), named by node id.

## 3. Theme and UI kit
- Pick a screen with the richest UI (sheets, buttons, list rows). Read it with get_jsx (Paper) or get_design_context (Figma).
- Write `design/user-flow/ui_kit.py` starting from `templates/project/ui_kit.py`. Copy the real values: font, ink and muted colours, the brand colour, radii, the button shapes, list rows, the status bar, and any signature block (like Argo's red top).
  - Every part is a small function that returns HTML. Explorations build screens only from these parts.
- Set `theme.accent` to the brand colour and `theme.font` to the font family in `config.json`.
- Check it imports: `cd design/user-flow/specs && python3 -c "import _uf, ui_kit"`.

## 4. Write the project folder
Copy `templates/project/` into `design/user-flow/`, then fill in:
- `config.json`: sources (`screens_page`, `maps_page`, `explore_page`, each with its `_name`; `library_page` + `_name`; `promote_page`; `legacy_file_ids`), persona, theme, `screen_ids` (how the screens page names screens, and the fallback from `references/project-and-paper.md` → Screen ids), `rules` (copy, product, files), `plugin_version` (from `.claude-plugin/plugin.json`), `device_label`, and empty `maps`.
- `config.local.json`: `{"plugin_root": "<resolved plugin root>"}`. It's gitignored, one per machine.
- `gaps.json`: `{"gaps": []}`. `questions.json`: `{"questions": []}`. `boards/.gitkeep`, so git keeps the empty folder.
- `.gitignore`: copy `templates/project/gitignore` to `design/user-flow/.gitignore` (it ignores `refs/`, `out/`, `config.local.json`).

Then run `python3 design/user-flow/specs/_uf.py` to check the bootstrap finds the plugin (it prints nothing and exits 0), and `python3 design/user-flow/specs/_uf.py status` for the first status block.

## 5. Finish
- If the repo has rules about new folders or files (AGENTS.md, CLAUDE.md, CONTRIBUTING), check them and add a line that allows `design/user-flow/`.
- Commit if the repo's conventions allow it; don't push.
- Tell the user what was found, for example "42 screens in 11 chapters, codebase has 12 routes". Suggest the next step: **map-master** for the whole app, or **map-journey** for one area.
