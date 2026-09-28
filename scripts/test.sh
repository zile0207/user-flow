#!/usr/bin/env bash
# Renders the fixture project with this checkout's lib/uf and compares every element hash with tests/expected.
# Usage: scripts/test.sh            check
#        scripts/test.sh --update   accept the current output as expected (only after reviewing the change)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/tests/fixture"
TMP="$(mktemp -d)"; cp -R "$SRC/" "$TMP/"          # specs may write to the registry: never touch the fixture itself
FIX="$TMP/design/user-flow"
export USER_FLOW_ROOT="$REPO"
cd "$FIX/specs"
fail=0
for pair in journey:journey master:master states:states explore:explore promote:promoted_j1; do
  spec="${pair%%:*}"; boardname="${pair#*:}"
  python3 "$spec.py" > /dev/null
  python3 - "$FIX" "$REPO/tests/expected" "$boardname" "${1:-}" <<'PY' || fail=1
import json, os, shutil, sys
fix, exp_dir, spec, mode = sys.argv[1:5]
man = json.load(open(os.path.join(fix, 'out', spec, 'manifest.json')))
exp_path = os.path.join(exp_dir, spec + '.json')
got = {'size': man['size'], 'elements': man['elements']}
if mode == '--update' or not os.path.exists(exp_path):
    json.dump(got, open(exp_path, 'w'), indent=1); print(f'{spec}: expected written ({len(got["elements"])} elements)'); sys.exit(0)
exp = json.load(open(exp_path))
if exp == got:
    print(f'{spec}: ok ({len(got["elements"])} elements)'); sys.exit(0)
e = dict(exp['elements']); g = dict(got['elements'])
changed = [k for k in g if k in e and e[k] != g[k]]
print(f'{spec}: CHANGED · size {exp["size"]} → {got["size"]} · changed {changed[:8]} · new {[k for k in g if k not in e][:8]} · gone {[k for k in e if k not in g][:8]}')
sys.exit(1)
PY
done
rm -rf "$TMP"
exit $fail
