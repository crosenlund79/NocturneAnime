"""Atlas -- blue amphibious humanoid from assets/references/atlas_reference.jpg.

From the portrait: blue skin with dark hatched shading, swept-back dark navy hair with a curled
forelock and long locks past the shoulders, big spined head fins at ear level, glowing pale eyes,
heavy brows, a highlighted nose, fanged smirk, stubble, and pale-cyan light streaks everywhere.
Outfit from assets/references/Atlas_1..4.jpg (clothing sketches): a fitted sleeveless fishnet top with
a deep V neck and an angular hem pointing to the navel, a dark V-shaped choker, short shorts with a
spiky fringe hem, fishnet stockings and stacked loose hoop bangles. Bare webbed feet and the forearm
fins keep him aquatic.
"""
import math
from rig import (Frame, smooth, line, taper, g, tr, rot, streaks, arm_chain, leg_chain, torso_group,
                 far, document, NECK)

SKIN, SKIN_SH, SKIN_DK = '#5b8fc6', '#36609a', '#24427a'
SKIN_HI = '#8fc3ec'
STREAK = '#d8f6ff'
HAIR, HAIR_SH, HAIR_HI = '#1a2647', '#0d1429', '#3d6db2'
FIN, FIN_SH, FIN_SPINE = '#88abd3', '#5a7fae', '#1a2647'
EYE, EYE_GLOW, IRIS = '#f4fdff', '#bff3ff', '#9cc9dc'
LIP = '#2a3f6e'
VEST, VEST_SH, VEST_HI = '#1d2a4d', '#111a33', '#3b5590'
TRIM, TRIM_SH = '#38c6c4', '#1f8f9a'
SASH, SASH_SH = '#36c9c2', '#1d8d94'
PANTS, PANTS_SH, PANTS_HI = '#2b3a5e', '#1a2440', '#4a5f8f'
WRAP, WRAP_SH = '#b9cadb', '#7f95b0'
PEARL = '#eef6ff'
CHAR_SCALE = 1.0


# ------------------------------------------------------------------- head
def fin(F, ang, spines, base, membrane_fill, shade):
    """A spined fin: base point list + spine tips; scalloped membrane between spines."""
    pts = [base[0]]
    for i, tip in enumerate(spines):
        pts.append(tip + (1,))
        if i < len(spines) - 1:
            nxt = spines[i + 1]
            mid = ((tip[0] + nxt[0]) / 2, (tip[1] + nxt[1]) / 2)
            cx, cy = base[1]
            pts.append((mid[0] + (cx - mid[0]) * 0.28, mid[1] + (cy - mid[1]) * 0.28))  # scallop
    pts.append(base[-1])
    d = smooth(pts)
    cx, cy = base[1]
    det = ''.join(line(f'M{cx:.1f},{cy:.1f} Q{(cx + t[0]) / 2 + 2:.1f},{(cy + t[1]) / 2 - 2:.1f} {t[0]:.1f},{t[1]:.1f}', 2.4, FIN_SPINE)
                  for t in spines)
    for t in spines[:-1]:
        mx, my = (cx * 0.45 + t[0] * 0.55), (cy * 0.45 + t[1] * 0.55)
        a = math.degrees(math.atan2(t[1] - cy, t[0] - cx))
        det += streaks(mx, my + 5, a, 3, 11, 3.2, 1.3, STREAK)
    return F.part(d, membrane_fill, shade, ang, 5, det, sw=2.6)


def head_back(F, ang, P):
    """Fins + back hair: drawn behind the face."""
    s = []
    lag = P['hair_lag']
    # far fin peeks out past the far temple (foreshortened)
    s.append(far(fin(F, ang, [(70, -96 + lag * .3), (84, -74), (86, -52), (76, -30)],
                     [(30, -70), (34, -54), (32, -38)], FIN, FIN_SH)))
    # back hair mass: swept back, long
    hair = smooth([(30, -76), (20, -104), (-8, -116), (-38, -104), (-56, -78), (-60, -48), (-56, -18),
                   (-50, 12 + lag), (-36, 20 + lag, 1), (-30, -6), (-20, -30), (-10, -48)])
    det = (streaks(-38, -70, -60, 4, 18, 4, 1.6, STREAK) + streaks(-50, -20, -95, 4, 20, 4, 1.6, STREAK)
           + line('M-10,-90 Q-40,-84 -52,-52', 1.5) + line('M-24,-60 Q-44,-40 -46,0', 1.5))
    s.append(F.part(hair, HAIR, HAIR_SH, ang, 6, det, sw=3.0, rim=HAIR_HI))
    # near fin, attached where the ear would be, spreading back and out
    s.append(fin(F, ang, [(-80, -104 + lag * .4), (-104, -80), (-110, -54), (-98, -28), (-76, -12)],
                 [(-26, -66), (-30, -48), (-26, -32)], FIN, FIN_SH))
    return ''.join(s)


def eye(F, cx, cy, w, h, outer_left, blink):
    o = -1 if outer_left else 1
    xo, xi = cx + o * w * 0.55, cx - o * w * 0.45
    if blink >= 0.95:
        return taper([(xo, cy + 1), (cx, cy + 4), (xi, cy)], 3, 2, 4.5)
    top = cy - h * 0.5 + h * blink * 0.8
    white = smooth([(xo, cy, 1), (cx + o * w * 0.15, top), (xi, top + 3), (xi, cy + 2, 1), (cx, cy + h * 0.45)])
    ecid = F.id('e')
    F.defs.append(f'<clipPath id="{ecid}"><path d="{white}"/></clipPath>')
    icx = cx - o * 1.5
    # pale glowing eye: no dark iris, just a faint ring and a pinpoint
    inner = (f'<ellipse cx="{icx}" cy="{cy + 1}" rx="{w * .2}" ry="{h * .5}" fill="none" stroke="{IRIS}" stroke-width="1.2"/>'
             f'<circle cx="{icx}" cy="{cy + 1}" r="1.1" fill="#6a9ab0"/>'
             f'<path d="M{xo},{top - 6} H{xi} V{top + 2.5} H{xo} Z" fill="{IRIS}" opacity=".45"/>')
    out = (f'<path d="{white}" fill="{EYE_GLOW}" filter="url(#glow)" opacity=".9"/>'
           f'<path d="{white}" fill="{EYE}"/><g clip-path="url(#{ecid})">{inner}</g>')
    out += taper([(xo + o * 2, cy + 1), (xo, cy - 1), (cx + o * w * 0.15, top - 1), (xi, top + 2), (xi - o * 1, cy + 1)], 2.5, 1.5, 5)
    out += line(smooth([(xo, cy + 1), (cx, cy + h * .5), (xi, cy + 3)], False), 2)
    return out


def head_front(F, ang, P):
    s = []
    blink = P['blink']
    neck = smooth([(-18, -28), (10, -18), (14, 22, 1), (-20, 22, 1)])
    neck_sh = f'<path d="{smooth([(-24, -30), (18, -12), (18, 2), (-24, 8)])}" fill="{SKIN_SH}"/>'
    neck_det = line('M-6,0 Q-2,10 -4,20', 1.4, SKIN_DK) + streaks(-8, 12, -15, 3, 10, 3, 1.3, STREAK)
    s.append(F.part(neck, SKIN, SKIN_SH, ang, 5, neck_sh + neck_det, sw=2.8))

    face = smooth([(-28, -66), (-16, -90), (14, -94), (36, -80), (42, -60), (44, -48), (49, -29, 1), (43, -24),
                   (40, -18), (34, -10), (20, 0, 1), (4, -2), (-12, -12), (-24, -28), (-29, -46)])
    hair_sh = f'<path d="{smooth([(-40, -62), (-6, -70), (16, -66), (34, -70), (50, -64), (50, -100), (-40, -100)])}" fill="{SKIN_SH}"/>'
    # stubble: hatching along the jaw / chin, like the reference's cross-hatched beard shadow
    hatch = ''
    for k in range(12):
        x = -14 + k * 3.6
        hatch += line(f'M{x:.1f},{-12 + abs(k - 7) * 0.9:.1f} l3,8', 1.0, SKIN_DK)
        hatch += line(f'M{x + 2:.1f},{-12 + abs(k - 7) * 0.9:.1f} l-3,8', 0.8, SKIN_DK)
    sockets = (f'<ellipse cx="2" cy="-45" rx="18" ry="10" fill="{SKIN_DK}" opacity=".55"/>'
               f'<ellipse cx="36" cy="-46" rx="10" ry="9" fill="{SKIN_DK}" opacity=".55"/>')
    lights = (streaks(4, -78, -25, 5, 16, 3.6, 1.5, STREAK) + streaks(-8, -24, -30, 4, 13, 3.4, 1.4, STREAK)
              + streaks(36, -30, -30, 3, 9, 3, 1.3, STREAK))
    cheek = line('M-14,-34 Q-6,-22 4,-18', 1.3, SKIN_DK) + line('M30,-40 Q36,-30 34,-22', 1.2, SKIN_DK)
    s.append(F.part(face, SKIN, SKIN_SH, ang, 6, sockets + cheek + hatch + lights, sw=3.0, extra_shade=hair_sh, rim=SKIN_HI))

    s.append(eye(F, 2, -44, 25, 10, True, max(blink, .12)))
    s.append(eye(F, 34, -45, 11, 9, False, max(blink, .12)))
    # heavy brows, angled down toward the nose
    s.append(taper([(-14, -54), (0, -58), (17, -54)], 3, 4, 6.5))
    s.append(taper([(27, -55), (35, -59), (44, -57)], 4.5, 2, 5))
    # nose with the bright bridge highlight from the reference
    s.append(line('M27,-42 Q30,-34 34,-27', 1.6, SKIN_DK))
    s.append(line('M38,-44 L45,-31', 1.8, STREAK))
    s.append(line('M33,-25 Q37,-22 42,-24', 1.6))
    # fanged smirk: dark lips, white teeth band with two small fangs; far corner raised
    mouth = smooth([(14, -13, 1), (26, -15), (38, -17, 1), (34, -10), (24, -8)])
    teeth = (f'<path d="M12,-16 H40 V-11.5 Q26,-10 12,-11.5 Z" fill="#ffffff"/>'
             f'<path d="M19,-12 l2,4 l2,-4 Z M31,-12.5 l2,4 l2,-4.4 Z" fill="#ffffff"/>')
    s.append(F.part(mouth, '#14203c', None, ang, 0, teeth, sw=2.2))
    s.append(line('M12,-13 Q24,-17 39,-18', 2.6, LIP) + line('M16,-6 Q25,-3 33,-7', 2.0, LIP))

    # front hair: centre part with the curled forelock falling on the forehead
    front = smooth([(-30, -58), (-42, -86), (-24, -112), (8, -120), (34, -108), (48, -88), (50, -72, 1), (36, -84),
                    (24, -78), (16, -64, 1), (10, -80), (-2, -86), (-14, -74), (-20, -52, 1), (-24, -68)])
    fsh = f'<path d="{smooth([(-40, -70), (0, -84), (40, -84), (50, -60), (-40, -50)])}" fill="{HAIR_SH}"/>'
    fdet = (streaks(-8, -104, -25, 5, 24, 3.6, 1.6, STREAK) + streaks(28, -98, 10, 4, 16, 3.4, 1.4, STREAK)
            + line('M4,-114 Q-18,-100 -24,-64', 1.5) + line('M20,-110 Q4,-96 4,-84', 1.4) + line('M34,-104 Q30,-92 34,-84', 1.3))
    s.append(F.part(front, HAIR, HAIR_SH, ang, 5, fdet, sw=3.0, extra_shade=fsh, rim=HAIR_HI))
    curl = taper([(12, -84), (20, -74), (18, -62), (10, -58), (8, -64)], 7, 2, 7)
    s.append(F.part(curl, HAIR, HAIR_SH, ang, 3, streaks(16, -74, 70, 2, 8, 3, 1.2, STREAK), sw=2.2))
    # loose wisps floating around the head
    lag = P['hair_lag']
    for pts in ([(-44, -30), (-62, -14 + lag), (-66, 8 + lag)], [(36, -96), (50, -100), (60, -92 + lag * .5)]):
        s.append(line(smooth(pts, False), 1.3, HAIR))
    return ''.join(s)


# ------------------------------------------------------------------- body
def long_hair(F, P):
    """Locks flowing down the back from under the skull, lagging with movement (torso space)."""
    out = []
    wind, ph = P['wind'], P['phase']
    for k, (ln, x0, w0, off) in enumerate([(130, -22, 30, 0.0), (112, -8, 24, 0.3), (96, -32, 22, 0.6)]):
        pts, x, y = [], x0, -176
        a = 96 + wind * 34 - k * 4
        for i in range(8):
            pts.append((x, y))
            f = i / 7
            a_i = a + 10 * f * math.sin(2 * math.pi * (ph + off) - f * 3.4) * (0.4 + wind) + f * 8 * wind
            x += ln / 7 * math.cos(math.radians(a_i))
            y += ln / 7 * math.sin(math.radians(a_i))
        pts.append((x, y))
        d = taper(pts, w0, 3, w0 + 4)
        det = streaks(pts[3][0], pts[3][1], a + 90, 4, w0 * .6, 3.6, 1.5, STREAK) + streaks(pts[6][0], pts[6][1], a + 90, 3, w0 * .4, 3.2, 1.3, STREAK)
        out.append(F.part(d, HAIR if k != 2 else HAIR_SH, HAIR_SH if k != 2 else '#070c1a', 0, 6, det, sw=2.6))
    return ''.join(out[::-1])


def net(F, x0, y0, w, h):
    """Fishnet lattice in the current bone space (an SVG pattern, so it moves with the limb)."""
    if not getattr(F, 'net_id', None):
        F.net_id = 'atnet'
        F.defs.append(f'<pattern id="atnet" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                      f'<path d="M0,0 H8 M0,0 V8" stroke="{VEST}" stroke-width="1.7" fill="none"/>'
                      f'<circle cx="0" cy="0" r="1.1" fill="{VEST}"/></pattern>')
    return (f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{VEST}" opacity=".16"/>'
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#atnet)"/>')


def piping(d, w=4.0):
    """Navy edge binding with a thin teal core."""
    return line(d, w, VEST, 'round') + line(d, w * .35, TRIM, 'round')


def torso(F, ang, P):
    s = []
    body = smooth([(-48, -126), (-16, -152), (28, -152), (46, -138), (50, -112), (42, -86), (30, -56),
                   (32, -24), (34, 6), (-32, 8), (-34, -22), (-28, -58), (-40, -100)])
    chest = (line('M20,-140 Q22,-110 20,-92', 1.8, SKIN_DK)               # sternum
             + line('M-8,-112 Q8,-100 20,-104', 1.6, SKIN_DK) + line('M22,-104 Q34,-100 42,-108', 1.5, SKIN_DK)
             + line('M4,-46 Q16,-43 28,-46', 1.4, SKIN_DK) + line('M14,-60 L14,-30', 1.2, SKIN_DK)   # abs
             + f'<path d="M17,-36 q2,4 0,6" stroke="{SKIN_DK}" stroke-width="1.6" fill="none"/>'         # navel
             + streaks(2, -126, -20, 4, 14, 3.6, 1.5, STREAK) + streaks(34, -122, -20, 3, 10, 3.2, 1.3, STREAK)
             + streaks(-12, -46, -20, 3, 10, 3.2, 1.3, STREAK))
    s.append(F.part(body, SKIN, SKIN_SH, ang, 9, chest, sw=3.2, rim=SKIN_HI))
    # fitted sleeveless fishnet top: deep V neck, angular hem pointing down to the navel
    top = smooth([(-46, -130), (-24, -150), (-8, -151, 1), (18, -100, 1), (28, -151, 1), (40, -147), (49, -128),
                  (47, -104), (40, -86, 1), (16, -56, 1), (-30, -76, 1), (-36, -96), (-44, -112)])
    tdet = (net(F, -60, -160, 120, 110)
            + piping('M-8,-150 L18,-101 L28,-150', 4.2)                    # V neckline
            + piping('M40,-86 L16,-57 L-30,-76', 3.6)                      # angular hem
            + piping('M-44,-128 L-22,-150', 3.2) + piping('M40,-147 L48,-129', 3.2))   # shoulder straps
    s.append(F.part(top, SKIN, SKIN_SH, ang, 9, tdet, sw=3.0, rim=SKIN_HI))
    return ''.join(s)


def choker(F, ang, P):
    """Dark V-shaped collar at the throat (torso space, drawn over the neck)."""
    d = smooth([(-8, -152, 1), (26, -154, 1), (22, -146), (12, -128, 1), (-3, -144)])
    det = line('M-6,-150 L12,-131 L24,-152', 1.4, TRIM) + f'<circle cx="12" cy="-135" r="2.2" fill="{PEARL}"/>'
    return F.part(d, VEST, VEST_SH, ang, 3, det, sw=2.6, rim=VEST_HI)


def shorts(F, ang, P):
    """Seat of the short shorts with a slim aqua belt and a small pouch (torso space)."""
    d = smooth([(-35, -30), (34, -36), (37, -8), (32, 8), (-30, 10), (-36, -8)])
    det = (line('M-34,-26 Q0,-33 35,-32', 6, SASH, 'butt') + line('M-34,-23 Q0,-30 35,-29', 1.2, SASH_SH, 'butt')
           + f'<rect x="-28" y="-20" width="11" height="12" rx="2" fill="{VEST}" stroke="#1c1424" stroke-width="1.6"/>'
           + line('M14,-22 Q16,-6 12,8', 1.4, PANTS_SH))
    return F.part(d, PANTS, PANTS_SH, ang, 6, det, sw=2.8, rim=PANTS_HI)


def bangles(ys, rx=15, ry=4.5, front=True, beads=False):
    """Loose hoop bracelets around a limb: back halves go under the limb, front halves over it."""
    out = ''
    for k, y in enumerate(ys):
        tilt = (-1) ** k * 4
        sweep = 0 if front else 1
        d = f'M{-rx},{y - tilt * .3:.1f} A{rx},{ry} {tilt} 0 {sweep} {rx},{y + tilt * .3:.1f}'
        out += line(d, 4.6, '#1c1424') + line(d, 2.4, WRAP)
        if front and beads:
            out += f'<circle cx="{rx * .3:.1f}" cy="{y + ry * .95:.1f}" r="2.6" fill="{PEARL}" stroke="#1c1424" stroke-width="1.4"/>'
    return out


def upper_arm(F):
    def draw(a):
        d = smooth([(-17, -6), (-3, -20), (14, -13), (17, 4), (13, 50), (10, 88, 1), (-11, 88, 1), (-15, 40)])
        det = (line('M-12,6 Q-6,0 4,4', 4, SKIN_DK) + line('M-14,16 Q-6,12 6,16', 3, SKIN_DK)   # dark banding
               + streaks(2, 26, -20, 3, 10, 3, 1.3, STREAK))
        ys = (40, 49)
        return (bangles(ys, 18, 5, front=False) + F.part(d, SKIN, SKIN_SH, a, 6, det, sw=3.0, rim=SKIN_HI)
                + bangles(ys, 18, 5, front=True, beads=True))
    return draw


def forearm(F):
    def draw(a):
        fin_d = smooth([(-12, 10), (-30, 22, 1), (-24, 32), (-33, 44, 1), (-20, 50), (-24, 60, 1), (-11, 58)])
        fin_det = line('M-12,16 L-28,23 M-12,36 L-30,44 M-12,52 L-22,59', 1.6, FIN_SPINE)
        d = smooth([(-11, -8), (11, -8), (11, 36), (8, 86, 1), (-8, 86, 1), (-11, 36)])
        det = line('M-10,8 Q-4,4 6,8', 2.6, SKIN_DK) + streaks(2, 34, -20, 3, 9, 3, 1.2, STREAK)
        ys = (64, 72, 80)
        return (F.part(fin_d, FIN, FIN_SH, a, 3, fin_det, sw=2.2) + bangles(ys, 14, 4.2, front=False)
                + F.part(d, SKIN, SKIN_SH, a, 5, det, sw=3.0, rim=SKIN_HI) + bangles(ys, 14, 4.2, front=True))
    return draw


def hand(F):
    def draw(a):
        d = smooth([(-9, -4), (9, -4), (12, 12), (12, 26), (10, 38, 1), (6, 33), (3, 41, 1), (-1, 34), (-4, 40, 1),
                    (-7, 32), (-10, 34, 1), (-11, 16)])
        det = (f'<path d="M6,30 L10,37 L3,38 Z M-1,31 L3,39 L-4,38 Z" fill="{FIN}"/>'  # webbing between fingers
               + line('M-6,6 Q0,10 8,6', 1.2, SKIN_DK))
        thumb = smooth([(6, 2), (15, 8), (17, 18), (10, 16)])
        return (F.part(d, SKIN, SKIN_SH, a, 4, det, sw=2.6)
                + F.part(thumb, SKIN, SKIN_SH, a, 2, '', sw=2.2))
    return draw


def thigh(F, P):
    def draw(a):
        d = smooth([(19, -20), (24, 10), (22, 60), (18, 110), (16, 134), (0, 144), (-16, 134), (-19, 100),
                    (-24, 50), (-25, 10), (-21, -20)])
        det = net(F, -30, 50, 60, 100) + line('M-25,56 Q0,62 23,54', 5, VEST) + line('M-25,56 Q0,62 23,54', 1.4, TRIM)
        leg = F.part(d, SKIN, SKIN_SH, a, 8, det, sw=3.0, rim=SKIN_HI)
        # shorts leg with a spiky fringe hem that swings a little
        sw = math.sin(2 * math.pi * P['phase']) * 2.5 * (0.3 + P['moving'])
        hem = [(22, 40), (17, 45), (10, 47), (3, 48), (-4, 48), (-11, 47), (-18, 45), (-24, 40)]
        fringe = ''.join(f'<path d="M{x - 3:.1f},{y - 2:.1f} L{x + sw * (1 + k % 2):.1f},{y + 13 + 3 * (k % 2):.1f} L{x + 3:.1f},{y - 2:.1f} Z" fill="{PANTS}" stroke="#1c1424" stroke-width="1.5" stroke-linejoin="round"/>'
                         for k, (x, y) in enumerate(hem))
        sh = smooth([(20, -20), (25, 10), (24, 38), (18, 44), (-4, 48), (-24, 42), (-26, 10), (-21, -20)])
        sdet = line('M-4,4 Q0,24 -4,40', 1.4, PANTS_SH) + line('M-24,36 Q0,44 23,34', 1.6, PANTS_HI)
        return leg + fringe + F.part(sh, PANTS, PANTS_SH, a, 8, sdet, sw=3.0, rim=PANTS_HI)
    return draw


def shin(F):
    def draw(a):
        d = smooth([(-17, -12), (17, -12), (16, 30), (12, 80), (10, 124, 1), (-12, 124, 1), (-16, 80),
                    (-21, 30)])
        det = (net(F, -30, -20, 60, 140)
               + line('M-20,0 Q0,8 20,-2', 1.4, SKIN_DK) + streaks(4, 40, -20, 3, 9, 3, 1.2, STREAK)
               + line('M-14,116 L12,114', 6, VEST, 'butt') + line('M-14,113 L12,111', 1.3, TRIM, 'butt'))  # ankle band
        return F.part(d, SKIN, SKIN_SH, a, 6, det, sw=3.0, rim=SKIN_HI)
    return draw


def foot(F):
    def draw(a):
        d = smooth([(-14, -10), (10, -10), (30, 2), (46, 8), (48, 16, 1), (-16, 18, 1), (-18, 2)])
        det = (line('M30,8 L32,17 M38,9 L39,17', 1.4, SKIN_DK)
               + f'<path d="M40,6 Q50,10 48,16 L42,16 Z" fill="{FIN}"/>')
        return F.part(d, SKIN, SKIN_SH, a, 4, det, sw=2.8, rim=SKIN_HI)
    return draw


def render(P, scale=1.0):
    F = Frame()
    ta = P['torso']
    arm = lambda side: arm_chain(P, side, upper_arm(F), forearm(F), hand(F), hand_scale=1.0)
    leg = lambda side: leg_chain(P, side, thigh(F, P), shin(F), foot(F))
    head_g = lambda fn: torso_group(P, g(tr(*NECK, P['head']) + ' scale(.97)', fn(F, ta + P['head'], P)))
    body = ''.join([
        torso_group(P, long_hair(F, P)),
        far(torso_group(P, arm('f')), leg('f')),
        torso_group(P, torso(F, ta, P)),
        leg('n'),
        torso_group(P, shorts(F, ta, P)),
        head_g(head_back),
        head_g(head_front),
        torso_group(P, choker(F, ta, P)),
        torso_group(P, arm('n')),
    ])
    return document(F, body, scale, CHAR_SCALE)


def idle(P):
    """Atlas's idle: relaxed, loose arms, weight on the back leg."""
    b = P['breath']
    P.update(sh_n=10 - 2 * b, el_n=-14 - 2 * b, wr_n=-4, sh_f=-6 + 2 * b, el_f=-16 - 2 * b, wr_f=-2)
    return P
