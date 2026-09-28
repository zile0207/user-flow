"""<App> UI kit for exploration screens. init fills this from the app's confirmed screens (get_jsx / get_design_context).
Replace every value below with the real one. This starter is Argo's kit, kept as a worked example of the level of detail needed.

Use these instead of writing raw HTML, so every exploration matches the confirmed look:
Switzer, ink #171B1D, muted #4B585B / #67787C, coral #E05254, sheet radius 32, pill buttons 52 tall.
"""
from uf.base import t, INK, MUTED, LINE

CORAL = '#E05254'   # Argo's brand coral

A = 'https://app.paper.design/file-assets/01M3KBWAY1R62GZASWQV3EEQS0/'
PHOTO = {  # photo assets already in the confirmed file
    'neon': A + '14W715EG2DSRSGS28AZXM5BXJV.jpg',      # neon bar, used as a TikTok video
    'night_market': A + '1476V86R25Y8FPSRFYSDM8VYP7.jpg',  # Kok Sen, Bedok 85, hawker at night
    'stall': A + '7QS9WXR0X6RMMAZGQHAKDQWQE0.jpg',     # Chomp Chomp, a lit stall
}
G = '#67787C'; G2 = '#9CA8AB'; SOFT = '#F1F3F3'
PW, PH = 390, 844

ICON = {
    'heart': 'M12 20.4C7 17 3.6 14 3.6 10.3A4.3 4.3 0 0 1 12 8.1a4.3 4.3 0 0 1 8.4 2.2c0 3.7-3.4 6.9-8.4 10.1z',
    'chat': 'M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z',
    'bookmark': 'M6 3h12v18l-6-4-6 4z',
    'share': 'M14 5l6 6-6 6M20 11H9a5 5 0 0 0-5 5v3',
    'check': 'M20 6 9 17l-5-5',
    'lock': 'M6 11h12v9H6zM8.5 11V8a3.5 3.5 0 0 1 7 0v3',
    'alert': 'M12 9v4M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z',
    'link': 'M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1',
    'search': 'M11 17.5a6.5 6.5 0 1 0 0-13 6.5 6.5 0 0 0 0 13zM20 20l-4.2-4.2',
    'arrow': 'M5 12h14M13 6l6 6-6 6',
}


def ico(name_or_path, size=22, col='#FFFFFF', sw=2):
    p = ICON.get(name_or_path, name_or_path)
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24"><path d="{p}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def status(time='6:38', dark=False):
    c = INK if dark else '#FFFFFF'
    return ('<div style="position:absolute;left:0;top:0;width:390px;height:54px;display:flex;align-items:center;justify-content:space-between;padding:0 24px 0 30px;box-sizing:border-box">'
            + t(time, 16, 21, 700, c) +
            f'<div style="display:flex;align-items:center;gap:7px"><svg width="18" height="13" viewBox="0 0 18 13"><rect x="0" y="8" width="3" height="5" rx="1" fill="{c}"/><rect x="5" y="5.5" width="3" height="7.5" rx="1" fill="{c}"/><rect x="10" y="3" width="3" height="10" rx="1" fill="{c}"/><rect x="15" y="0" width="3" height="13" rx="1" fill="{c}"/></svg>'
            f'<svg width="25" height="13" viewBox="0 0 25 13"><rect x="0.6" y="0.6" width="21" height="11.8" rx="3.4" fill="none" stroke="{c}" stroke-opacity="0.55" stroke-width="1.2"/><rect x="2.4" y="2.4" width="17.4" height="8.2" rx="2.2" fill="{c}"/></svg></div></div>')


def dim():
    return '<div style="position:absolute;left:0;top:0;width:390px;height:844px;background:#00000073"></div>'


def host_video(user, caption, photo='neon', time='6:38'):
    """A TikTok or Instagram video behind a share sheet, dimmed."""
    rail = ''.join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:3px">{ico(p, 30)}' + t(n, 12, 14, 600, '#FFFFFF') + '</div>'
                   for p, n in [('heart', '12.4K'), ('chat', '318'), ('bookmark', '2,041'), ('share', 'Share')])
    return (f'<div style="position:absolute;left:0;top:0;width:390px;height:844px;background-image:url({PHOTO[photo]});background-size:cover;background-position:50%"></div>'
            '<div style="position:absolute;left:0;top:420px;width:390px;height:424px;background-image:linear-gradient(180deg,#00000000,#000000B3)"></div>'
            f'<div style="position:absolute;left:334px;top:330px;display:flex;flex-direction:column;gap:18px;align-items:center">{rail}</div>'
            '<div style="position:absolute;left:16px;top:700px;width:300px;display:flex;flex-direction:column;gap:4px">'
            + t(user, 15, 20, 700, '#FFFFFF') + t(caption, 14, 19, 500, '#FFFFFF') + '</div>' + status(time) + dim())


def host_web(title, domain, blurb, photo='night_market', time='6:38'):
    """A web page behind a share sheet, dimmed."""
    return ('<div style="position:absolute;left:0;top:0;width:390px;height:844px;background:#F6F1EA"></div>'
            '<div style="position:absolute;left:20px;top:110px;width:350px;display:flex;flex-direction:column;gap:14px">'
            + t(title, 28, 33, 700, '#2B2B2B') + t(domain, 13, 18, 600, '#8A8178') +
            f'<div style="height:200px;border-radius:14px;background-image:url({PHOTO[photo]});background-size:cover"></div>'
            + t(blurb, 16, 23, 500, '#4A4540') + '</div>' + status(time, dark=True) + dim())


def phone(name, behind, front):
    """One 390x844 screen. `name` becomes the layer name, e.g. 'A·1 · Sent'."""
    return (f'<div layer-name="{name}" style="position:relative;width:390px;height:844px;overflow:clip;background:#000000;flex-shrink:0">'
            + behind + front +
            '<div style="position:absolute;left:128px;top:830px;width:134px;height:5px;border-radius:3px;background:#171B1D"></div></div>')


def sheet(h, body, bg='#FFFFFF'):
    return (f'<div style="position:absolute;left:0;top:{PH-h}px;width:390px;height:{h}px;background:{bg};border-radius:32px 32px 0 0;display:flex;flex-direction:column;overflow:clip">'
            + body + '</div>')


def col(gap, inner, pad='24px 20px 0 20px'):
    return f'<div style="display:flex;flex-direction:column;gap:{gap}px;padding:{pad}">{inner}</div>'


def row(gap, inner, align='center'):
    return f'<div style="display:flex;gap:{gap}px;align-items:{align}">{inner}</div>'


def grow(inner, gap=3):
    return f'<div style="flex:1;display:flex;flex-direction:column;gap:{gap}px">{inner}</div>'


def btn(label, kind='primary', w='100%'):
    if kind == 'primary':
        return f'<div style="height:52px;width:{w};border-radius:26px;background:{INK};display:flex;align-items:center;justify-content:center">' + t(label, 16, 20, 700, '#FFFFFF') + '</div>'
    if kind == 'soft':
        return f'<div style="height:52px;width:{w};border-radius:26px;background:{SOFT};display:flex;align-items:center;justify-content:center">' + t(label, 16, 20, 700, INK) + '</div>'
    return f'<div style="height:40px;width:{w};display:flex;align-items:center;justify-content:center">' + t(label, 15, 20, 700, INK) + '</div>'


def thumb(photo, w=56, h=88, r=12, extra=''):
    return f'<div style="width:{w}px;height:{h}px;border-radius:{r}px;background-image:url({PHOTO.get(photo, photo)});background-size:cover;background-position:50%;flex-shrink:0;{extra}"></div>'


def eyebrow(s): return t(s, 13, 18, 600, G)
def title(s, size=24): return t(s, size, size + 5, 700, INK, 'letter-spacing:-0.022em;')
def body(s): return t(s, 15, 21, 500, MUTED)
def small(s): return t(s, 13, 18, 500, G)


def spinner(size=14, c=CORAL, track=LINE):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="{track}" stroke-width="3"/><path d="M12 3a9 9 0 0 1 9 9" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"/></svg>'


def badge(icon, bg, fg='#FFFFFF', size=44):
    return f'<div style="width:{size}px;height:{size}px;border-radius:{size//2}px;background:{bg};display:flex;align-items:center;justify-content:center;flex-shrink:0">{ico(icon, 22, fg, 2.4)}</div>'


def tick(on=True):
    if on:
        return f'<div style="width:24px;height:24px;border-radius:12px;background:{CORAL};display:flex;align-items:center;justify-content:center;flex-shrink:0">{ico("check", 14, "#FFFFFF", 3)}</div>'
    return '<div style="width:24px;height:24px;border-radius:12px;border:2px solid #C9D0D2;box-sizing:border-box;flex-shrink:0"></div>'


def place_row(photo, name, quote, picked=True):
    return row(12, thumb(photo, 48, 48, 10) + grow(t(name, 16, 21, 700, INK) + small(quote), 0) + tick(picked))


def board_row(photo, name, sub, picked=False):
    th = thumb(photo, 40, 40, 9) if photo else f'<div style="width:40px;height:40px;border-radius:9px;border:1.5px dashed #B4BDBF;box-sizing:border-box;display:flex;align-items:center;justify-content:center">{ico("link", 18, G, 2)}</div>'
    return f'<div style="display:flex;align-items:center;gap:12px;height:48px">' + th + grow(t(name, 16, 21, 700, INK) + small(sub), 0) + tick(picked) + '</div>'


def skeleton_row():
    return (f'<div style="display:flex;align-items:center;gap:12px;opacity:0.7"><div style="width:48px;height:48px;border-radius:10px;background:{SOFT}"></div>'
            f'<div style="display:flex;flex-direction:column;gap:8px"><div style="width:148px;height:12px;border-radius:6px;background:{LINE}"></div><div style="width:96px;height:10px;border-radius:5px;background:{SOFT}"></div></div></div>')


def note_box(s):
    return '<div style="background:#F5F6F6;border-radius:12px;padding:12px">' + t(s, 13, 18, 500, MUTED) + '</div>'


def search_field(placeholder):
    return f'<div style="height:48px;border-radius:24px;background:{SOFT};display:flex;align-items:center;gap:10px;padding:0 16px">' + ico('search', 18, G, 2) + t(placeholder, 15, 20, 500, G2) + '</div>'


def red_top(inner):
    """Argo's coral top block, as a card inside a sheet."""
    return f'<div style="background:{CORAL};padding:22px 20px 20px 20px;display:flex;gap:14px;align-items:center;border-radius:32px">{inner}</div>'


def progress(done_px, total_px=170, label=''):
    return (f'<div style="display:flex;align-items:center;gap:8px"><div style="width:{total_px}px;height:4px;border-radius:2px;background:#FFFFFF4D">'
            f'<div style="width:{done_px}px;height:4px;border-radius:2px;background:#FFFFFF"></div></div>' + t(label, 12, 16, 600, '#FDF3F3') + '</div>')
