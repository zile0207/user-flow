#!/usr/bin/env bash
set -euo pipefail

# Links every skill into ~/.agents/skills for Codex and other Agent Skills-compatible harnesses.
# Claude Code users install the plugin instead (/plugin marketplace add zile0207/user-flow), which namespaces
# the skills as user-flow:<name>. That matters because Claude Code has a built-in /init.
# Pass --claude to also link into ~/.claude/skills (init is linked there as user-flow-init).
# Each entry is a symlink into this repo, so `git pull` keeps them current.
# Skills find the plugin root by resolving their own symlink, so lib/ and references/ still work.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DESTS=("$HOME/.agents/skills")
[ "${1:-}" = "--claude" ] && DESTS+=("$HOME/.claude/skills")

for DEST in "${DESTS[@]}"; do
  mkdir -p "$DEST"
  for skill_md in "$REPO"/skills/*/SKILL.md; do
    src="$(dirname "$skill_md")"
    name="$(basename "$src")"
    [ "$DEST" = "$HOME/.claude/skills" ] && [ "$name" = "init" ] && name="user-flow-init"
    target="$DEST/$name"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "skip $target: a real folder is already there" >&2
      continue
    fi
    ln -sfn "$src" "$target"
    echo "linked $name -> $src ($DEST)"
  done
done
