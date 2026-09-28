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
- **Where maps and explorations go:** a page in the same file. Offer to create one called "User Journey".
- **The persona:** a name and a line about them. Offer to draft it from a story or spec page if one exists.
- **The router,** if there's a codebase: Expo Router, Next.js app router, React Navigation, or other. Detect it first, then confirm.

## 2. Read the sources
- **Paper:** get_basic_info for the screens page. List the artboards (the chapters) and the screens inside each, with their node ids. Screen IDs come from the page's own naming (chapter·step) where it has one.
- **Figma:** the Figma MCP. List the frames on the screens page, with their node ids.
- **Codebase:** walk the routes folder. Each route is a screen; `ref` is the route path.

Don't export any images yet. The map skills export what they draw.

## 3. Theme and UI kit
- Pick a screen with the richest UI (sheets, buttons, list rows). Read it with get_jsx (Paper) or get_design_context (Figma).
- Write `design/user-flow/ui_kit.py` starting from `templates/project/ui_kit.py`. Copy the real values: font, ink and muted colours, the brand colour, radii, the button shapes, list rows, the status bar, and any signature block (like Argo's red top).
  - Every part is a small function that returns HTML. Explorations build screens only from these parts.
- Set `theme.accent` to the brand colour and `theme.font` to the font family in `config.json`.

## 4. Write the project folder
Copy `templates/project/` into `design/user-flow/`, then fill in:
- `config.json`: sources, persona, theme, and empty `maps`.
- `config.local.json`: `{"plugin_root": "<resolved plugin root>"}`. It's gitignored, one per machine.
- `gaps.json`: `{"gaps": []}`.
- `.gitignore`: `img/`, `refs/`, `out/`, `config.local.json`.

Then run `python3 design/user-flow/specs/_uf.py` to check the bootstrap finds the plugin. It should print nothing and exit 0.

## 5. Finish
- If the repo has rules about new folders or files (AGENTS.md, CLAUDE.md, CONTRIBUTING), check them and add a line that allows `design/user-flow/`.
- Commit if the repo's conventions allow it; don't push.
- Tell the user what was found, for example "42 screens in 11 chapters, codebase has 12 routes". Suggest the next step: **map-master** for the whole app, or **map-journey** for one area.
