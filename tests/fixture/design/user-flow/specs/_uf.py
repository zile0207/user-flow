"""Bootstrap for specs: finds the user-flow plugin and loads this project. Every spec starts with `from _uf import P`."""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _plugin_root():
    if os.environ.get('USER_FLOW_ROOT'):
        return os.environ['USER_FLOW_ROOT']
    local = os.path.join(ROOT, 'config.local.json')
    if os.path.exists(local):
        return json.load(open(local))['plugin_root']
    home = os.path.expanduser('~')
    for hit in sorted(glob.glob(f'{home}/.claude/plugins/marketplaces/*/lib/uf') + glob.glob(f'{home}/.claude/plugins/cache/*/user-flow/*/lib/uf')):
        return os.path.dirname(os.path.dirname(hit))
    raise RuntimeError('user-flow plugin not found. Set USER_FLOW_ROOT or run the init skill.')


sys.path.insert(0, os.path.join(_plugin_root(), 'lib'))
sys.path.insert(0, ROOT)          # the project's ui_kit.py
from uf.project import load  # noqa: E402

P = load(ROOT)
