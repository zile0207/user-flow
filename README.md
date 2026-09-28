# user-flow

Map every screen of an app in [Paper](https://paper.design), find the ones that are missing, and design them.

- **Master map:** every screen, grouped by area. What exists and what's missing.
- **Journey map:** one area end to end, drawn as a flowchart. The persona's path is the spine, and every other way through branches off it.
- **Flow map:** one job to be done, from "when I…" to "job done".
- **Audit:** walks a map against a coverage checklist (errors, empty states, permissions, waiting, returning, undo). Each missing screen becomes a numbered gap, `N2·3`.
- **Explore:** takes a gap to its own board: references (yours, or from Mobbin), three directions built in the app's real UI, rounds of iteration, then confirm. The confirmed screen replaces the gap on every map.

Every board is generated from code (`lib/uf`), so it looks the same whichever agent draws it, Claude or GPT.

## Install

**Claude Code**
```
/plugin marketplace add zile0207/user-flow
/plugin install user-flow@user-flow
```

**Codex and other Agent Skills harnesses**
```
git clone https://github.com/zile0207/user-flow && user-flow/scripts/link-skills.sh
```

Needs the Paper MCP. Figma sources need the Figma MCP. Reference search uses the Mobbin MCP. The renderer needs Python 3.9+ and has no dependencies.

## Skills

| Skill | Invoked by | What it does |
|---|---|---|
| [`user-flow`](skills/user-flow/SKILL.md) | you | The index. Describe what you want and it routes to the right skill. |
| [`init`](skills/init/SKILL.md) | you | Sets up `design/user-flow/` in a project: sources, persona, theme, UI kit. |
| [`map-master`](skills/map-master/SKILL.md) | you or the agent | Every screen in the app, grouped by area. |
| [`map-journey`](skills/map-journey/SKILL.md) | you or the agent | One area end to end, every branch and gap. |
| [`map-flow`](skills/map-flow/SKILL.md) | you or the agent | One job to be done, start to done. |
| [`audit-flow`](skills/audit-flow/SKILL.md) | you or the agent | Finds missing screens in a map and adds them as gaps. |
| [`map-states`](skills/map-states/SKILL.md) | you or the agent | Every state one surface can show, in priority order, and the rule that picks one. |
| [`explore-design`](skills/explore-design/SKILL.md) | you or the agent | Designs a gap: references, 3 directions, rounds, confirm. |
| [`promote-design`](skills/promote-design/SKILL.md) | you or the agent | Moves a confirmed design onto the screens page with stable screen ids. |
| [`answer-questions`](skills/answer-questions/SKILL.md) | you or the agent | Takes answers to open questions and applies what each one changes. |
| [`sync-board`](skills/sync-board/SKILL.md) | you or the agent | Updates a board on the canvas to match its spec: only what changed, after checking for hand edits. |

In Claude Code the skills are namespaced: `/user-flow:user-flow`, `/user-flow:init`, and so on.

## How it fits together

```
init ──> map-master ──> map-journey ──> map-flow        map-states
              │              │              │                │
              └──── audit-flow (gaps N<journey>·<n>, questions Q<journey>·<n>) ───┘
                             │                        │
                     explore-design ──> confirm   answer-questions
                             │
                      promote-design ──> screens page (X2·1) ──> developers

every change ──> sync-board (only what changed; stops on hand edits)
```

A project keeps its own files in `design/user-flow/`:
- `config.json`: sources, theme, persona, maps
- `gaps.json` and `questions.json`: the gap and question registries
- `boards/`: what is painted on each board, for sync
- `ui_kit.py`: the app's screen parts
- `specs/`: one file per board

Images and rendered output are gitignored and can be re-created. See [references/project-and-paper.md](references/project-and-paper.md).

## Repo

```
.claude-plugin/   plugin and marketplace manifests
skills/           one folder per skill: SKILL.md, plus agents/openai.yaml for Codex
lib/uf/           renderers: jmap.py (journeys, flows), master.py, states.py, explore.py, promote.py; board.py (keys and sync); project.py (config, registries)
references/       rules the skills follow: nodes and layout, explore board, design review, coverage checklist, sync, project and Paper
templates/        project starter files, plus worked examples from Argo
scripts/          link-skills.sh, test.sh (regression test against tests/fixture)
tests/            a fixture project and the expected element hashes
```
