"""Minimal UI kit for the test fixture."""
from uf.base import t, INK, MUTED


def phone(name, body):
    return f'<div layer-name="{name}" style="position:relative;width:390px;height:844px;background:#FFFFFF;flex-shrink:0">' + body + '</div>'


def title(s):
    return t(s, 24, 29, 700, INK)
