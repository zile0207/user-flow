# Maintaining user-flow

`CLAUDE.md` is a symlink to this file. Claude and GPT agents both work on this repo.

- **Skills** live in `skills/<name>/SKILL.md`, each with an `agents/openai.yaml`.
  - `user-flow` and `init` are user-invoked. Keep `disable-model-invocation: true` and `policy.allow_implicit_invocation: false` in sync for them.
  - The other skills are model-invoked, with trigger-rich descriptions.
- **Adding or renaming a skill** means updating four places together:
  - `.claude-plugin/plugin.json` → `skills`
  - the table in `README.md`
  - the table and routing rules in `skills/user-flow/SKILL.md`. The router must never point at a skill that doesn't exist, or miss one that does.
  - the naming: `{action}-{slug}` (`map-flow`, `audit-flow`, `explore-design`). `init` and `user-flow` are the exceptions.
- **Skills find shared files** by resolving their own real directory and going two levels up to the plugin root. Don't use `../other-skill/` paths.
- **`lib/uf` is the only place that draws.** A layout change goes into the renderer and `references/nodes-and-layout.md` together.
  - Before committing, run `scripts/test.sh`. It renders `tests/fixture` and compares every element hash, then runs `tests/test_lib.py` (sync plans, drift, the registries, the command line). An intended visual change: review it, run `scripts/test.sh --update`, and bump the version (boards painted with the old version will show replaces on their next sync).
  - A change to how `board.py` hashes or keys elements must keep older committed states working (see `format` in the manifest and `test_legacy_state_upgrades_with_renames`).
- **Registries are changed through `lib/uf/cli.py`** (`specs/_uf.py <command>`), never by calls inside a spec. Skills tell agents to use the command line, so Claude and GPT agents get identical results.
  - Keep `board.VERSION` and `.claude-plugin/plugin.json` → `version` equal.
- **Version:** bump `.claude-plugin/plugin.json` → `version` on every release. Claude Code uses it to show updates.
- **Validate** with `claude plugin validate . --strict` after touching a manifest.
