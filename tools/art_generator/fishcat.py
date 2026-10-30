"""Fishcat -- turquoise feline humanoid from assets/references/fishcat_reference.jpg.

From the drawing: turquoise skin with dark teal leopard spots, purple/magenta dreadlocks, tall cat
ears with peach insides and a gold hoop in her right ear, gold eyes with a black star-shaped scar
over the left one, peach lips with two small fangs, a choker strap crossing into an X over the
chest, a long flowing yellow dress with a V-pointed bodice and ochre fold lines, clawed hands with
pink palms, a curled tail with a tufted spotted tip, and paws peeking out under the hem.
"""
import math
from rig import (Frame, smooth, line, taper, g, tr, rot, blobs, arm_chain, leg_chain, torso_group, far,
                 document, to_world, knee_world, NECK, GROUND, INK)

SKIN, SKIN_SH, SKIN_HI = '#62cfcf', '#3a9fae', '#a6ecea'
SPOT = '#2b7f96'
PEACH, PEACH_SH = '#f6a896', '#d97a74'
HAIR, HAIR_SH, HAIR_HI, HAIR_PINK = '#9467c7', '#62409a', '#b98ae0', '#d36fc9'
EYE, EYE_SH = '#f0b21e', '#a8650c'
GOLD = '#f2c230'
DRESS, DRESS_SH, DRESS_FOLD, DRESS_HI = '#f2c64e', '#d39a2a', '#c27d16', '#ffe28e'
CHAR_SCALE = 0.93


# ------------------------------------------------------------------- head
def loc(F, ang, pts, w, pink=False):
    """One dreadlock: a tapered strand with segment ticks (and a magenta streak on some)."""
    d = taper(pts, w, w * 0.75, w * 1.05)
    det = ''
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
        a = math.atan2(y1 - y0, x1 - x0)
        nx, ny = -math.sin(a) * w * .5, math.cos(a) * w * .5
        det += line(f'M{pts[i][0] - nx:.1f},{pts[i][1] - ny:.1f} Q{pts[i][0] + math.cos(a) * 3:.1f},{pts[i][1] + math.sin(a) * 3:.1f} {pts[i][0] + nx:.1f},{pts[i][1] + ny:.1f}', 1.1, HAIR_SH)
    if pink:
        det += line(smooth(pts[1:], False), w * .3, HAIR_PINK)
    return F.part(d, HAIR, HAIR_SH, ang, 3, det, sw=2.2, rim=HAIR_HI)


def strand(root, mid, end, lag, n=6):
    """Points along a quadratic curve root->end; lower points swing by lag."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = (1 - t) ** 2 * root[0] + 2 * (1 - t) * t * mid[0] + t * t * end[0]
        y = (1 - t) ** 2 * root[1] + 2 * (1 - t) * t * mid[1] + t * t * end[1]
        out.append((x - lag * t * t, y))
    return out


def ear(F, ang, base0, base1, tip, earring=False):
    d = smooth([base0, tip + (1,), base1])
    inner = smooth([((base0[0] * 2 + base1[0]) / 3, (base0[1] * 2 + base1[1]) / 3 - 2),
                    (tip[0] * .85 + (base0[0] + base1[0]) / 2 * .15, tip[1] * .85 + (base0[1] + base1[1]) / 2 * .15 + 4, 1),
                    ((base0[0] + base1[0] * 2) / 3, (base0[1] + base1[1] * 2) / 3 - 2)])
    det = f'<path d="{inner}" fill="{PEACH}"/>' + line(smooth([(tip[0] + 2, tip[1] + 14), (tip[0] + 4, tip[1] + 22)], False), 1, '#ffffff')
    out = F.part(d, SKIN, SKIN_SH, ang, 4, det, sw=2.6)
    if earring:
        x, y = base0[0] + (tip[0] - base0[0]) * .25, base0[1] + (tip[1] - base0[1]) * .25
        out += (f'<circle cx="{x - 4:.1f}" cy="{y + 4:.1f}" r="6" fill="none" stroke="{INK}" stroke-width="4.5"/>'
                f'<circle cx="{x - 4:.1f}" cy="{y + 4:.1f}" r="6" fill="none" stroke="{GOLD}" stroke-width="2.4"/>')
    return out


def cat_eye(F, cx, cy, w, h, outer_left, blink):
    o = -1 if outer_left else 1
    xo, xi = cx + o * w * 0.55, cx - o * w * 0.45
    if blink >= 0.95:
        return taper([(xo, cy + 1), (cx, cy + 4), (xi, cy)], 3, 2, 4.5)
    top = cy - h * 0.55 + h * blink * 0.85
    white = smooth([(xo, cy - 3, 1), (cx + o * w * .1, top), (xi, top + 4), (xi, cy + 2, 1), (cx, cy + h * .45)])
    ecid = F.id('e')
    F.defs.append(f'<clipPath id="{ecid}"><path d="{white}"/></clipPath>')
    icx = cx - o * 1
    iris = (f'<ellipse cx="{icx}" cy="{cy}" rx="{w * .36}" ry="{h * .62}" fill="{EYE}"/>'
            f'<path d="M{xo},{cy - h} H{xi} V{top + 4} H{xo} Z" fill="{EYE_SH}"/>'
            f'<ellipse cx="{icx}" cy="{cy + .5}" rx="1.6" ry="{h * .42}" fill="#2a1406"/>'
            f'<ellipse cx="{icx}" cy="{cy}" rx="{w * .36}" ry="{h * .62}" fill="none" stroke="#7a4a08" stroke-width="1.2"/>'
            f'<circle cx="{icx + o * w * .12}" cy="{cy - h * .22}" r="{max(1.4, w * .08)}" fill="#ffffff"/>')
    out = f'<path d="{white}" fill="#fffbea"/><g clip-path="url(#{ecid})">{iris}</g>'
    out += taper([(xo + o * 3, cy - 1), (xo, cy - 4), (cx + o * w * .1, top - 1), (xi, top + 3), (xi - o, cy + 1)], 2.5, 1.5, 5.5)
    out += taper([(xo + o, cy - 4), (xo + o * 7, cy - 9)], 3.5, 1)
    out += line(smooth([(xo, cy - 1), (cx, cy + h * .5), (xi, cy + 2)], False), 1.5)
    return out


def head_back(F, ang, P):
    s = []
    lag = P['hair_lag'] * 1.6 + P['wind'] * 6
    for root, mid, end, w, pink in [((-30, -96), (-60, -60), (-64, 6), 11, True), ((-44, -82), (-68, -40), (-70, 14), 10, False),
                                    ((-10, -104), (-48, -70), (-50, 12), 11, False), ((6, -104), (-28, -60), (-36, 14), 10, True),
                                    ((22, -100), (50, -66), (54, 6), 11, False), ((34, -90), (58, -50), (60, 12), 10, True)]:
        s.append(loc(F, ang, strand(root, mid, end, lag), w, pink))
    s.append(far(ear(F, ang, (14, -92), (34, -82), (40, -128))))
    s.append(ear(F, ang, (-30, -80), (-6, -94), (-34, -132), earring=True))
    return ''.join(s)


def head_front(F, ang, P):
    s = []
    blink = P['blink']
    neck = smooth([(-16, -26), (8, -16), (12, 20, 1), (-16, 20, 1)])
    s.append(F.part(neck, SKIN, SKIN_SH, ang, 4, f'<path d="{smooth([(-20, -30), (16, -12), (14, 2), (-20, 6)])}" fill="{SKIN_SH}"/>', sw=2.6))
    face = smooth([(-28, -64), (-18, -88), (12, -92), (34, -80), (40, -62), (42, -46), (44, -34, 1), (40, -30),
                   (38, -20), (30, -10), (16, -4, 1), (2, -8), (-12, -16), (-24, -30), (-29, -46)])
    spots = blobs([(-20, -52, 1.3), (-14, -72, 1.1), (2, -82, .9), (20, -84, .8), (-24, -34, 1.2), (-10, -26, .8),
                   (-26, -64, .9), (38, -62, .7), (30, -76, .6)], SPOT)
    hair_sh = f'<path d="{smooth([(-40, -64), (0, -74), (40, -72), (50, -96), (-40, -100)])}" fill="{SKIN_SH}"/>'
    s.append(F.part(face, SKIN, SKIN_SH, ang, 5, spots, sw=3.0, extra_shade=hair_sh, rim=SKIN_HI))
    s.append(cat_eye(F, 2, -46, 27, 18, True, blink))
    # far eye with the star-shaped scar from the reference
    s.append(cat_eye(F, 34, -47, 12, 15, False, blink))
    star = smooth([(34, -64, 1), (36.5, -50), (46, -47, 1), (36.5, -44), (33, -32, 1), (31.5, -44), (24, -47, 1), (31.5, -50)])
    s.append(f'<path d="{star}" fill="{INK}" opacity=".88"/><circle cx="34" cy="-47" r="3.2" fill="{EYE}"/>'
             + line('M28,-40 L22,-30 M37,-38 L41,-28', 1.4))
    s.append(line('M-12,-58 Q-2,-62 12,-58', 2.2) + line('M28,-59 Q34,-62 42,-60', 2))
    s.append(line('M42,-34 L45,-31 L41,-30', 1.8))  # nose
    # big peach lips with a small fang at each side
    lips = smooth([(16, -22, 1), (26, -25), (38, -24, 1), (39, -17), (32, -11), (22, -11), (16, -16)])
    s.append(F.part(lips, PEACH, PEACH_SH, ang, 2, line('M18,-19 Q28,-16 38,-19', 1.8, '#8a3a3a'), sw=2.2))
    s.append('<path d="M20,-18.5 l1.6,4 l1.6,-3.6 Z M34,-18.8 l1.4,3.8 l1.6,-3.8 Z" fill="#ffffff" stroke="#1c1424" stroke-width=".8"/>')
    # scalp cap + front locs framing the face
    cap = smooth([(-34, -70), (-32, -98), (0, -110), (32, -100), (42, -80), (22, -88), (0, -90), (-20, -84)])
    s.append(F.part(cap, HAIR, HAIR_SH, ang, 4, line('M-16,-100 Q0,-92 12,-102', 1.2, HAIR_SH), sw=2.6, rim=HAIR_HI))
    lag = P['hair_lag'] * 1.2 + P['wind'] * 4
    for root, mid, end, w, pink in [((-18, -96), (-34, -64), (-34, -12), 11, False), ((-26, -90), (-44, -56), (-46, -2), 10, True),
                                    ((-4, -100), (6, -82), (2, -66), 10, True), ((12, -100), (24, -84), (28, -70), 9, False),
                                    ((32, -94), (52, -72), (58, -40), 9, True)]:
        s.append(loc(F, ang, strand(root, mid, end, lag * (.5 if end[1] < -50 else 1)), w, pink))
    return ''.join(s)


# ------------------------------------------------------------------- body
def torso(F, ang, P):
    s = []
    body = smooth([(-40, -124), (-12, -150), (24, -150), (40, -136), (42, -112), (34, -86), (26, -56),
                   (30, -24), (32, 4), (-30, 6), (-32, -24), (-26, -58), (-34, -98)])
    det = blobs([(-30, -130, 1.1), (-22, -118, .8), (36, -128, .9), (40, -116, .6)], SPOT)
    det += line('M-38,-122 l-4,-3 l1,5 l-5,-1 l4,4', 1.4) + line('M38,-130 l5,-2 l-2,4 l5,0', 1.4)  # fur tufts
    det += line('M-6,-140 Q6,-134 16,-140', 1.3, SKIN_SH)
    s.append(F.part(body, SKIN, SKIN_SH, ang, 8, det, sw=3.0, rim=SKIN_HI))
    # crossed straps from the choker to the bodice corners
    strap = '#e8b93e'
    s.append(line('M-2,-150 Q8,-136 36,-118', 7) + line('M-2,-150 Q8,-136 36,-118', 4, strap))
    s.append(line('M26,-150 Q14,-136 -24,-118', 7) + line('M26,-150 Q14,-136 -24,-118', 4, strap))
    s.append(line('M-10,-152 Q10,-146 30,-152', 7) + line('M-10,-152 Q10,-146 30,-152', 4, strap))
    return ''.join(s)


def bodice(F, ang, P):
    s = []
    # bodice: straight neckline, sides down to a V point at the waist
    bodice = smooth([(-34, -118, 1), (42, -118, 1), (36, -86), (30, -56), (34, -46, 1), (14, -30, 1),
                     (-30, -44, 1), (-28, -60), (-34, -96)])
    bdet = (line('M-30,-112 Q-28,-80 -24,-52', 1.4, DRESS_FOLD) + line('M30,-112 Q32,-82 26,-54', 1.4, DRESS_FOLD)
            + line('M-30,-114 L40,-114', 2, DRESS_HI))
    s.append(F.part(bodice, DRESS, DRESS_SH, ang, 8, bdet, sw=3.0, rim=DRESS_HI))
    return ''.join(s)


def skirt(F, P):
    """Long skirt in world space, draped from the hips over the forward knee to a trailing hem.
    The hem lags behind the legs so the fabric swings while walking."""
    mv = P['moving']
    sway = math.sin(2 * math.pi * (P['cycle'] - 0.18)) * 9 * mv + math.sin(2 * math.pi * P['phase']) * 1.5 * (1 - mv)
    bk, fr = to_world(P, (-34, -40)), to_world(P, (36, -42))
    bh, fh = to_world(P, (-38, -6)), to_world(P, (38, -10))
    xs = [P['ank_n'][0], P['ank_f'][0]]
    kn = max(knee_world(P, 'n')[0], knee_world(P, 'f')[0])
    # hem hangs from the lowest foot (so it follows the legs in a jump), billows up with `flare`
    # and pools wider in a crouch
    floor = max(P['ank_n'][1], P['ank_f'][1]) + 18 if P.get('air') else GROUND
    fl, cr = P.get('flare', 0.0), P.get('crouch', 0.0)
    front_hem = (max(xs) + 50 + sway * .6 + fl * 26 + cr * 16, floor - 17 - fl * 34)
    back_hem = (min(xs) - 70 + sway * 1.4 - 14 * mv - fl * 24 - cr * 12, floor - 1 - fl * 46)
    front_mid = (max(fh[0] + 8, kn + 20), (fh[1] + front_hem[1]) / 2)
    back_mid = (bh[0] - 10 + sway * .5 - 6 * mv, (bh[1] + back_hem[1]) / 2)
    hem = []
    for i in range(1, 6):
        t = i / 6
        x = front_hem[0] + (back_hem[0] - front_hem[0]) * t
        y = front_hem[1] + (back_hem[1] - front_hem[1]) * t * t + fl * 14 * math.sin(t * math.pi) + 3 * math.sin(t * math.pi * 3 + P['cycle'] * 6.28)
        hem.append((x, y))
    pts = [bk, fr, fh, front_mid, front_hem + (1,)] + hem + [back_hem + (1,), back_mid, bh]
    d = smooth(pts)
    folds = ''
    for i in range(6):
        t = (i + .5) / 6
        top = (fr[0] + (bk[0] - fr[0]) * t, fr[1] + (bk[1] - fr[1]) * t + 14)
        bot = (front_hem[0] + (back_hem[0] - front_hem[0]) * t, front_hem[1] + (back_hem[1] - front_hem[1]) * t - 6)
        mid = ((top[0] + bot[0]) / 2 + sway * .4 * (1 - t), (top[1] + bot[1]) / 2)
        y0 = top[1] + (bot[1] - top[1]) * (0.12 + 0.18 * (i % 2))
        x0 = top[0] + (bot[0] - top[0]) * (0.12 + 0.18 * (i % 2))
        folds += line(f'M{x0:.1f},{y0:.1f} Q{mid[0]:.1f},{mid[1]:.1f} {bot[0]:.1f},{bot[1]:.1f}', 2.2, DRESS_FOLD)
        if i % 2:
            folds += f'<path d="M{bot[0] - 7:.1f},{bot[1] + 8:.1f} Q{mid[0]:.1f},{mid[1]:.1f} {bot[0]:.1f},{bot[1] - 40:.1f} Q{mid[0] + 5:.1f},{mid[1] + 20:.1f} {bot[0] + 6:.1f},{bot[1] + 8:.1f} Z" fill="{DRESS_SH}" opacity=".55"/>'
    folds += line(smooth([(front_hem[0] - 6, front_hem[1] - 3)] + [(x, y - 3) for x, y in hem] + [(back_hem[0] + 8, back_hem[1] - 3)], False), 2, DRESS_HI)
    return F.part(d, DRESS, DRESS_SH, 0, 9, folds, sw=3.2, rim=DRESS_HI)


def tail(F, P):
    """Curled tail from behind the hips with a tufted, spotted tip (torso space)."""
    mv, ph = P['moving'], P['phase']
    pts, x, y = [], -24, -18
    for i in range(10):
        pts.append((x, y))
        a = 172 + i * 12 + 8 * math.sin(2 * math.pi * ph - i * .5) * (0.6 + mv) - mv * 10 * i / 9
        x += 14 * math.cos(math.radians(a))
        y += 14 * math.sin(math.radians(a))
    pts.append((x, y))
    d = taper(pts, 13, 9, 11)
    det = blobs([(pts[4][0], pts[4][1], .7), (pts[7][0], pts[7][1], .6)], SPOT)
    tx, ty = pts[-1]
    a = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
    ux, uy = math.cos(a), math.sin(a)
    tuft = smooth([(tx - ux * 4 - uy * 7, ty - uy * 4 + ux * 7), (tx + ux * 10 - uy * 10, ty + uy * 10 + ux * 10),
                   (tx + ux * 22, ty + uy * 22, 1), (tx + ux * 12 + uy * 11, ty + uy * 12 - ux * 11),
                   (tx - ux * 4 + uy * 7, ty - uy * 4 - ux * 7)])
    return (F.part(d, SKIN, SKIN_SH, 0, 4, det, sw=2.6, rim=SKIN_HI)
            + F.part(tuft, SKIN, SKIN_SH, 0, 4, blobs([(tx + ux * 10, ty + uy * 10, 1.1)], SPOT), sw=2.6))


def upper_arm(F):
    def draw(a):
        d = smooth([(-15, -6), (-2, -18), (13, -12), (15, 4), (12, 50), (10, 88, 1), (-11, 88, 1), (-14, 40)])
        det = blobs([(-6, 10, 1), (6, 24, .9), (-8, 40, 1.1), (4, 56, .8), (-4, 72, .9)], SPOT)
        return F.part(d, SKIN, SKIN_SH, a, 5, det, sw=2.8, rim=SKIN_HI)
    return draw


def forearm(F):
    def draw(a):
        d = smooth([(-11, -8), (11, -8), (10, 40), (8, 86, 1), (-8, 86, 1), (-12, 40), (-13, 6),
                    (-19, 0, 1), (-13, -2)])  # fur tuft at the elbow
        det = blobs([(-2, 10, .9), (4, 30, .8), (-4, 48, .9), (2, 66, .7)], SPOT)
        return F.part(d, SKIN, SKIN_SH, a, 5, det, sw=2.8, rim=SKIN_HI)
    return draw


def hand(F):
    def draw(a):
        d = smooth([(-9, -4), (9, -4), (12, 12), (12, 26), (9, 36, 1), (5, 30), (2, 38, 1), (-2, 30),
                    (-5, 37, 1), (-8, 28), (-11, 30, 1), (-11, 14)])
        det = f'<ellipse cx="2" cy="14" rx="8" ry="9" fill="{PEACH}"/>'  # pink palm
        claws = ''.join(f'<path d="M{x},{y} q1,5 -2,8 q0,-4 -2,-7 Z" fill="#2a2030"/>' for x, y in [(10, 35), (3, 37), (-4, 36), (-10, 29)])
        thumb = smooth([(6, 2), (15, 8), (16, 17), (10, 16)])
        return (F.part(d, SKIN, SKIN_SH, a, 4, det, sw=2.4) + claws
                + F.part(thumb, SKIN, SKIN_SH, a, 2, '', sw=2))
    return draw


def paw(F):
    def draw(a):
        d = smooth([(-14, -8), (12, -10), (30, 0), (40, 10), (38, 18, 1), (-14, 18, 1), (-16, 4)])
        det = (line('M24,10 Q26,15 23,18 M32,10 Q34,15 31,18', 1.6, SKIN_SH)
               + f'<path d="M38,15 l6,1 l-5,3 Z M31,16 l6,1 l-5,3 Z" fill="#2a2030"/>'
               + f'<ellipse cx="6" cy="15" rx="9" ry="3" fill="{PEACH}"/>' + blobs([(4, 2, .8), (20, 4, .6)], SPOT))
        return F.part(d, SKIN, SKIN_SH, a, 4, det, sw=2.6, rim=SKIN_HI)
    return draw


def render(P, scale=1.0):
    F = Frame()
    ta = P['torso']
    hidden = lambda a: ''  # legs are under the dress; only paws show
    arm = lambda side: arm_chain(P, side, upper_arm(F), forearm(F), hand(F), upper_len=84, fore_len=80, hand_scale=.95)
    leg = lambda side: leg_chain(P, side, hidden, hidden, paw(F))
    head_g = lambda fn: torso_group(P, g(tr(*NECK, P['head']) + ' scale(1.02)', fn(F, ta + P['head'], P)))
    body = ''.join([
        torso_group(P, tail(F, P)),
        far(torso_group(P, arm('f'))),
        far(leg('f')),
        leg('n'),
        torso_group(P, torso(F, ta, P)),
        skirt(F, P),
        torso_group(P, bodice(F, ta, P)),
        head_g(head_back),
        head_g(head_front),
        torso_group(P, arm('n')),
    ])
    return document(F, body, scale, CHAR_SCALE)


def idle(P):
    """Reference pose: right arm hanging with claws out, left hand on the hip."""
    b = P['breath']
    P.update(sh_n=6 - 2 * b, el_n=-10 - 2 * b, wr_n=6, sh_f=-38 + 1.5 * b, el_f=84 - 2 * b, wr_f=-20,
             ank_n=(178, GROUND - 18), ank_f=(222, GROUND - 22))
    return P


def walk(P):
    """Smaller arm swing and steps that suit the long dress."""
    for k in ('sh_n', 'sh_f'):
        P[k] = P[k] * .7
    return P
