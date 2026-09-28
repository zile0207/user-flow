"""Explore · N2·1 · Share to Argo. Render: python3 specs/explore_n2_1.py"""
from _uf import P
from uf.base import t, INK, MUTED, LINE
from uf.explore import render
from ui_kit import *

REF = P.refs_dir + '/'

# ---------------- screens (built only from argo_ui parts)
A1 = phone('A·1 · Sent', host_video('@thesmartlocal', 'No-queue hawkers after 9. Four stalls where the line is gone by 9:30.'),
           sheet(318, col(18,
               row(14, thumb('neon') + grow(eyebrow('@thesmartlocal on TikTok') + title('Sent to Argo') + row(7, spinner() + small('Reading now, about a minute'))) + badge('check', CORAL))
               + body('The places will be waiting in Argo. It tells you when they are ready.')
               + col(6, btn('Done') + btn('Open Argo', 'text'), pad='0'))))
A2 = phone('A·2 · The video is private', host_video('someone on Instagram', 'A reel you tapped Share on.', 'night_market'),
           sheet(318, col(18,
               row(14, badge('lock', SOFT, INK, 56) + grow(eyebrow('Someone on Instagram') + title("Argo can't open this one")))
               + body('The video is private: only followers can see it. Know the place in it? Type it in Argo.')
               + col(6, btn('Type the place in Argo') + btn('Close', 'text'), pad='0'))))

B1 = phone('B·1 · Reading, live', host_video('@thesmartlocal', 'No-queue hawkers after 9.'),
           sheet(600, red_top(grow(t('Reading your link', 21, 26, 700, '#FFFFFF', 'letter-spacing:-0.02em;') + t('No-queue hawkers after 9 · @thesmartlocal', 13, 18, 500, '#FDF3F3') + progress(94, 170, '0:32 of 0:58'), 6)
                                  + thumb('neon', 56, 88, 10, 'border:2px solid #FFFFFF;box-sizing:border-box;'))
                      + col(12, row(6, t('Found so far', 17, 22, 700, INK) + t('2', 17, 22, 500, G2), 'baseline')
                            + place_row('night_market', 'Bedok 85 Market', '“The queue is gone by 9:30”') + place_row('stall', 'Chomp Chomp', '“Satay until 1am on Fridays”') + skeleton_row()
                            + note_box('You can close this. Argo keeps reading and tells you when it is done.')
                            + row(10, btn('Open in Argo', 'soft', '50%') + btn('Done', 'primary', '50%')), pad='18px 20px 0 20px')))
B2 = phone('B·2 · The video is gone', host_video('@hawkerhunt', 'This video is no longer available.', 'stall'),
           sheet(600, red_top(grow(row(8, ico('alert', 20, '#FFFFFF', 2.4) + t("Couldn't read this link", 21, 26, 700, '#FFFFFF', 'letter-spacing:-0.02em;')) + t('@hawkerhunt on TikTok · sent just now', 13, 18, 500, '#FDF3F3'), 6))
                      + col(14, title('The video is gone', 20) + body('It was taken down from TikTok, so there is nothing left for Argo to read.')
                            + col(6, t('Remember the places in it?', 17, 22, 700, INK) + small('Type a name in Argo and it finds the place.'), pad='6px 0 0 0')
                            + search_field('Type a place name') + row(10, btn('Close', 'soft', '50%') + btn('Find the place', 'primary', '50%')), pad='22px 20px 0 20px')))

C1 = phone('C·1 · Pick a board', host_video('@thesmartlocal', 'No-queue hawkers after 9.'),
           sheet(560, col(16,
               row(12, thumb('neon', 40, 60, 8) + grow(title('Sent to Argo', 19) + row(7, spinner(12) + small('Reading No-queue hawkers after 9')), 2))
               + f'<div style="height:1px;background:{LINE}"></div>'
               + col(2, title('Where should its places go?', 19) + small('Argo adds them when it is done reading.'), pad='0')
               + col(6, board_row('night_market', 'Late-night zi char', '11 places · good fit') + board_row('stall', 'Supper runs', '5 places') + board_row(None, 'Decide later', 'Not in a board yet', True), pad='0')
               + col(4, btn('Done') + btn('+ New board', 'text'), pad='2px 0 0 0'))))
C2 = phone('C·2 · Not a video', host_web('The 12 best laksa in Singapore', 'sethlui.com', 'From Katong to Sungei Road, these are the bowls worth the queue this year.'),
           sheet(360, col(18,
               row(14, badge('link', SOFT, INK, 56) + grow(eyebrow('sethlui.com/best-laksa') + title("That's not a video")))
               + body('Argo reads TikTok and Instagram videos. This link is a web page, so there is nothing for it to watch.')
               + t('Send the video it came from instead.', 15, 21, 700, INK) + col(6, btn('Close'), pad='0'))))

SPEC = {
    'id': 'N2·1',
    'title': 'Share to Argo',
    'source': 'from Journey 2, row 2',
    'journey': {'name': 'Journey 2', 'artboard': '27RS-0', 'card_xy': (1540, 1080)},
    'status': {'state': 'confirmed', 'chosen': 'A', 'round': 1, 'date': 'Mon 28 Sep 2026'},
    'brief': {
        'needs': "Argo's panel in the iOS share sheet. Jamie is watching a video in TikTok or Instagram, taps Share, then Argo. Argo is closed. The panel says the link was sent and is being read, and says so there if the link won't work.",
        'musts': ['Confirms the link reached Argo', 'Says Argo is reading, and roughly how long',
                  "Says so right there if the link won't work, and what to do next", 'Gets Jamie back to the video fast', 'Works while Argo itself is closed'],
        'where': [('outside', 'OUTSIDE ARGO', 'Share → Argo'), ('this', 'N2·1 · THIS', 'Share to Argo'),
                  ('screen', REF + 'after_e63.png', 'E6·3 · Argo reads it', 'Still reading, in Argo')],
    },
    'refs_source': 'mobbin',
    'refs': [
        {'img': REF + 'matter.png', 'name': 'Matter', 'take': 'A saved card with one action, then gone', 'url': 'https://mobbin.com/screens/f687734e-8071-4afc-9402-e3ce35d16687'},
        {'img': REF + 'otter.png', 'name': 'Otter', 'take': 'A small sheet over the host app', 'url': 'https://mobbin.com/screens/9ed10e03-7a6d-4db9-a01b-2b8895fe0a2f'},
        {'img': REF + 'corner.png', 'name': 'corner', 'take': 'Pick where it goes while saving', 'url': 'https://mobbin.com/screens/d63cf8a0-4813-4a64-a420-fa0f9f61fef2'},
        {'img': REF + 'gphotos.png', 'name': 'Google Photos', 'take': 'Progress inside the sheet', 'url': 'https://mobbin.com/screens/6025d8fc-b3c0-43cd-bbec-25fe0decce28'},
        {'img': REF + 'cosmos.png', 'name': 'Cosmos', 'take': 'Teaching people to save from any app', 'url': 'https://mobbin.com/screens/4c4036d8-1eab-4227-bce2-5f8a37a3247f'},
        {'img': REF + 'sharesheet.png', 'name': 'iOS share sheet', 'take': 'Where Argo shows up in the first place', 'url': 'https://mobbin.com/screens/291953c7-3def-4b13-b111-622a4fba2e6b'},
    ],
    'rounds': [
        {'date': 'Mon 28 Sep', 'ask': None, 'directions': [
            {'letter': 'A', 'title': 'Sent, and gone', 'idea': 'A small card that confirms and gets out of the way. Jamie is back in TikTok in one tap.',
             'good': 'the fastest way back to the video. Nothing to decide.', 'costs': 'Jamie sees no places until Argo opens; the result lands later, in the top.',
             'inspired': 'Otter and Matter: a short saved card, one action.',
             'screens': [{'label': 'Sent', 'html': A1}, {'label': 'The video is private', 'html': A2}]},
            {'letter': 'B', 'title': 'Watch it read', 'idea': "Argo's red top comes into TikTok. Places appear as Argo finds them, like E6·3.",
             'good': 'shows Argo working and builds trust on the first shares.', 'costs': 'a tall sheet over the video, and it tempts Jamie to wait the full minute.',
             'inspired': 'E6·3 Still reading and the Google Photos progress sheet.',
             'screens': [{'label': 'Reading, live', 'html': B1}, {'label': 'The video is gone', 'html': B2}]},
            {'letter': 'C', 'title': 'Sent, now where?', 'idea': 'Confirm, then offer a board while the link is fresh. Decide later is the default.',
             'good': 'fewer places pile up in Not in a board yet.', 'costs': 'a choice before Argo knows what is in the video; one more tap.',
             'inspired': 'corner: pick a curation while saving.',
             'screens': [{'label': 'Pick a board', 'html': C1}, {'label': 'Not a video', 'html': C2}]},
        ]},
    ],
}

if __name__ == '__main__':
    render(P, 'explore_n2_1', SPEC)
