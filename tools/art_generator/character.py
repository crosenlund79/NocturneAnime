"""Original character "Homura Kagari" -- a procedurally posed, hand-authored vector cut-out rig.

Every body part is a hand-placed spline shape in its own bone space. A pose (a dict of
joint angles) is turned into one SVG frame. Cel shading is generated per part by
subtracting a copy of the shape shifted toward the world light, so the shadow side
stays consistent as limbs rotate. A dilated silhouette pass adds the heavy outer ink line.
"""
import math

W, H = 400, 640          # frame size in px
GROUND = 612             # y of the ground line in the frame
INK = '#1c1424'
LIGHT = (0.55, -0.83)    # world-space direction *toward* the key light (upper front)

# palette -------------------------------------------------------------------
SKIN, SKIN_SH = '#ffe2cc', '#f0a48e'
HAIR, HAIR_SH, HAIR_HI = '#323a86', '#1d2257', '#6a7fd6'
HAIR_TIP, HAIR_TIP2 = '#ff6a2a', '#ffd23f'
SUIT, SUIT_SH, SUIT_HI = '#2a2d45', '#181a2c', '#4b5078'
COAT, COAT_SH = '#e8283e', '#a3123a'
TRIM = '#f6f1e6'
GOLD, GOLD_SH = '#ffc832', '#d9821a'
GLOVE, GLOVE_SH, GLOVE_LN = '#34323f', '#1f1d29', '#6a6680'
SCARF, SCARF_SH = '#22c3cf', '#12809a'
IRIS, IRIS_SH, IRIS_LO = '#f7a823', '#a8430f', '#ffe27a'
MOUTH, TONGUE = '#7a1a2c', '#e8606e'


# ---------------------------------------------------------------- path helpers
def smooth(pts, closed=True, t=0.5):
    """Catmull-Rom spline through pts. A point (x, y, 1) is a sharp corner."""
    P = [(p[0], p[1], len(p) > 2) for p in pts]
    n = len(P)
    d = f'M{P[0][0]:.1f},{P[0][1]:.1f}'
    segs = n if closed else n - 1
    for i in range(segs):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        if not closed:
            p0 = P[max(i - 1, 0)]
            p3 = P[min(i + 2, n - 1)]
        k1 = 0 if p1[2] else t / 3 * 2
        k2 = 0 if p2[2] else t / 3 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k1 / 2, p1[1] + (p2[1] - p0[1]) * k1 / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k2 / 2, p2[1] - (p3[1] - p1[1]) * k2 / 2)
        d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d + (' Z' if closed else '')


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


class Frame:
    def __init__(self):
        self.defs, self.uid = [], 0

    def id(self, p):
        self.uid += 1
        return f'{p}{self.uid}'

    def part(self, d, fill, shade=None, ang=0.0, off=6.0, detail='', sw=3.0, extra_shade='', rim=None):
        """Filled shape + automatic cel shadow + clipped details + ink outline.
        ang: accumulated rotation of the bone (deg) so the light stays fixed in world space."""
        out = [f'<path d="{d}" fill="{fill}"/>']
        cid = self.id('c')
        self.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        inner = ''
        if shade:
            lx, ly = rot(LIGHT, -ang)
            mid = self.id('m')
            self.defs.append(
                f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="4000" height="4000">'
                f'<rect x="-2000" y="-2000" width="4000" height="4000" fill="#fff"/>'
                f'<path d="{d}" transform="translate({lx * off:.2f},{ly * off:.2f})" fill="#000"/></mask>')
            inner += f'<path d="{d}" fill="{shade}" mask="url(#{mid})"/>'
            inner += extra_shade
        if rim:  # thin lit-edge highlight: shape minus a copy nudged away from the light
            lx, ly = rot(LIGHT, -ang)
            rid = self.id('r')
            self.defs.append(
                f'<mask id="{rid}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="4000" height="4000">'
                f'<rect x="-2000" y="-2000" width="4000" height="4000" fill="#fff"/>'
                f'<path d="{d}" transform="translate({-lx * 3.2:.2f},{-ly * 3.2:.2f})" fill="#000"/></mask>')
            inner += f'<path d="{d}" fill="{rim}" mask="url(#{rid})"/>'
        inner += detail
        if inner:
            out.append(f'<g clip-path="url(#{cid})">{inner}</g>')
        out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
        return ''.join(out)


def line(d, w=2.2, c=INK, cap='round'):
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round"/>'


def taper(pts, w0, w1, w_mid=None):
    """Closed brush-stroke shape along a polyline, width tapering w0 -> (w_mid) -> w1."""
    n = len(pts)
    left, right = [], []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        f = i / (n - 1)
        if w_mid is None:
            w = w0 + (w1 - w0) * f
        else:
            w = (w0 + (w_mid - w0) * f * 2) if f < .5 else (w_mid + (w1 - w_mid) * (f - .5) * 2)
        left.append((p[0] + nx * w / 2, p[1] + ny * w / 2))
        right.append((p[0] - nx * w / 2, p[1] - ny * w / 2))
    return smooth(left + right[::-1])


def g(transform, *items):
    return f'<g transform="{transform}">' + ''.join(items) + '</g>'


def tr(x, y, a=0):
    return f'translate({x:.2f},{y:.2f}) rotate({a:.2f})'


# ------------------------------------------------------------------- the head
def head(F, ang, blink=0.0, hair_lag=0.0):
    """Head in neck-joint space. blink: 0 open .. 1 closed."""
    s = []
    hc = (-2, -58)  # cranium centre

    # -- back hair mass: broad flame locks sweeping up and back
    locks = [(-34, 66, -6, 30), (-62, 84, -16, 32), (-94, 94, -24, 34), (-126, 92, -26, 32),
             (-156, 84, -22, 30), (176, 74, -18, 30), (150, 62, -12, 26), (128, 48, -6, 20)]
    pts, strands = [], ''
    R0 = 52
    for i, (a, r, bend, w) in enumerate(locks):
        b = bend + hair_lag * (0.5 + i * 0.25)
        P = lambda ang, rad: (hc[0] + rad * math.cos(math.radians(ang)), hc[1] + rad * math.sin(math.radians(ang)))
        pts.append(P(a + w / 2, R0))                                  # valley (front side of lock)
        pts.append(P(a + w * 0.2 + b * 0.4, (R0 + r) / 2 + 5))         # convex leading edge
        pts.append(P(a + b, r) + (1,))                                 # sharp tip
        pts.append(P(a - w * 0.25 + b * 0.5, (R0 + r) / 2 - 3))        # concave trailing edge
        strands += line(smooth([P(a + w * .45, R0 - 8), P(a + w * .2 + b * .3, R0 + 4), P(a + b * .5, (R0 + r) / 2 + 2)], False), 1.6)
    pts.append(P(locks[-1][0] - locks[-1][3] / 2, R0 - 2))
    pts += [(-30, -16), (-12, -30), (18, -60), (34, -66)]
    hair_d = smooth(pts)
    def ring(r, amp):
        tip = []
        for k in range(60):
            a = k / 60 * 360
            rr = r + amp * math.sin(math.radians(a * 9))
            tip.append((hc[0] + rr * math.cos(math.radians(a)), hc[1] + rr * math.sin(math.radians(a))))
        return 'M-400,-400 H400 V400 H-400 Z ' + smooth(tip)
    tips = (f'<path d="{ring(60, 5)}" fill-rule="evenodd" fill="{HAIR_TIP}"/>'
            f'<path d="{ring(74, 4)}" fill-rule="evenodd" fill="{HAIR_TIP2}"/>')
    shine = []
    for k in range(11):  # jagged anime shine band
        a = -150 + k * 9
        shine.append((hc[0] + (42 if k % 2 == 0 else 34) * math.cos(math.radians(a)),
                      hc[1] + (42 if k % 2 == 0 else 34) * math.sin(math.radians(a)), 1))
    for k in range(11):
        a = -60 - k * 9
        shine.append((hc[0] + (31 if k % 2 == 0 else 28) * math.cos(math.radians(a)),
                      hc[1] + (31 if k % 2 == 0 else 28) * math.sin(math.radians(a)), 1))
    hi = f'<path d="{smooth(shine)}" fill="{HAIR_HI}"/>'
    s.append(F.part(hair_d, HAIR, HAIR_SH, ang, 8, tips + hi + strands, sw=3.2, rim=HAIR_HI))

    # -- neck
    neck = smooth([(-16, -26), (8, -18), (10, 20, 1), (-15, 20, 1)])
    chin_sh = f'<path d="{smooth([(-20, -30), (16, -14), (14, 0), (-20, 4)])}" fill="{SKIN_SH}"/>'
    s.append(F.part(neck, SKIN, SKIN_SH, ang, 4, chin_sh, sw=2.6))

    # -- ear (near side)
    ear = smooth([(-24, -56), (-36, -60), (-42, -48), (-38, -34), (-27, -30)])
    s.append(F.part(ear, SKIN, SKIN_SH, ang, 4, line(smooth([(-30, -52), (-37, -47), (-33, -38)], False), 1.6), sw=2.6))

    # -- face
    face = smooth([(-30, -64), (-18, -86), (12, -90), (36, -76), (42, -58), (44, -44), (40, -28),
                   (30, -13), (16, -3, 1), (2, -8), (-14, -18), (-26, -30), (-30, -44)])
    hair_shadow = f'<path d="{smooth([(-40, -60), (-10, -66), (14, -62), (30, -64), (46, -60), (46, -96), (-40, -96)])}" fill="{SKIN_SH}"/>'
    blush = ''.join(line(f'M{x},{y} l-3,6', 1.5, '#ff7f8a') for x, y in [(-8, -30), (-3, -30), (2, -30), (36, -31), (40, -31)])
    s.append(F.part(face, SKIN, SKIN_SH, ang, 5, '', sw=3.0, extra_shade=hair_shadow + blush))

    # -- eyes
    def eye(cx, cy, w, h, outer_left, irx):
        """outer_left: outer corner is on -x side (near eye)."""
        o = -1 if outer_left else 1
        xo, xi = cx + o * w * 0.55, cx - o * w * 0.45
        top = cy - h * 0.55
        bot = cy + h * 0.5
        if blink >= 0.95:  # closed: a happy curved lash line
            return taper([(xo, cy + 2), (cx, cy + 6), (xi, cy + 1)], 3, 2, 5)
        lid = top + (bot - top) * blink * 0.85
        white = smooth([(xo, cy - 1, 1), (cx + o * w * 0.2, lid), (xi, lid + 5, 1), (xi + o * 1, cy + h * .25, 1),
                        (cx, bot), (xo - o * 2, cy + h * .25)])
        ecid = F.id('e')
        F.defs.append(f'<clipPath id="{ecid}"><path d="{white}"/></clipPath>')
        icx = cx - o * 1.0
        iris = (f'<ellipse cx="{icx}" cy="{cy + 1}" rx="{irx}" ry="{h * 0.62}" fill="{IRIS}"/>'
                f'<ellipse cx="{icx}" cy="{cy + h * 0.32}" rx="{irx * 0.75}" ry="{h * 0.22}" fill="{IRIS_LO}"/>'
                f'<path d="M{icx - irx - 2},{cy - h} H{icx + irx + 2} V{cy - h * .08} Q{icx},{cy + h * .08} {icx - irx - 2},{cy - h * .08} Z" fill="{IRIS_SH}"/>'
                f'<ellipse cx="{icx}" cy="{cy + 1}" rx="{irx * 0.42}" ry="{h * 0.3}" fill="#3a1408"/>'
                f'<ellipse cx="{icx}" cy="{cy + 1}" rx="{irx}" ry="{h * 0.62}" fill="none" stroke="#5a1f0a" stroke-width="1.4"/>'
                f'<ellipse cx="{icx + o * irx * 0.35}" cy="{cy - h * 0.2}" rx="{irx * 0.38}" ry="{h * 0.17}" fill="#fff"/>'
                f'<circle cx="{icx - o * irx * 0.45}" cy="{cy + h * 0.3}" r="1.6" fill="#fff"/>'
                f'<path d="M{xo},{cy - h} H{xi} V{lid + 3.5} H{xo} Z" fill="#b9b2dc" opacity=".6"/>')
        out = f'<path d="{white}" fill="#fff"/><g clip-path="url(#{ecid})">{iris}</g>'
        # heavy upper lash line with a flick at the outer corner
        out += taper([(xo + o * 3, cy + 2), (xo, cy - 2), (cx + o * w * 0.2, lid - 1), (xi - o * 1, lid + 4), (xi - o * 1, lid + 8)], 3, 1.5, 7)
        out += taper([(xo + o * 2, cy - 2), (xo + o * 7, cy - 6)], 4, 1)   # lash flick
        out += line(smooth([(xo - o * 4, cy + h * .38), (cx, bot + 1), (xi + o * 2, cy + h * .3)], False), 1.6)
        return out

    s.append(eye(2, -42, 27, 20, True, 9))
    s.append(eye(34, -43, 15, 19, False, 6))
    # brows: determined, angled down toward the nose
    s.append(taper([(-14, -58), (0, -63), (17, -57)], 2.5, 3.5, 5.5))
    s.append(taper([(27, -58), (35, -63), (43, -63)], 3.5, 2, 4.5))
    # nose + mouth (open confident grin)
    s.append(line('M40,-34 L43,-27 L39,-25', 1.8))
    mouth = smooth([(18, -19, 1), (26, -18), (33, -21, 1), (30, -12), (24, -10)])
    s.append(F.part(mouth, MOUTH, None, ang, 0,
                    f'<path d="M16,-22 H36 V-17 Q26,-15.5 16,-17 Z" fill="#fff"/>'
                    f'<ellipse cx="25" cy="-10" rx="5" ry="3.5" fill="{TONGUE}"/>', sw=2.2))

    # -- bangs over the forehead
    bangs = smooth([(-30, -46), (-34, -72), (-10, -90), (22, -88), (44, -72), (47, -54, 1), (38, -64),
                    (32, -50, 1), (26, -66), (14, -52, 1), (8, -70), (-6, -54, 1), (-12, -70),
                    (-22, -34, 1), (-24, -58)])
    bang_sh = f'<path d="{smooth([(-40, -60), (-20, -70), (0, -72), (20, -70), (50, -70), (50, -40), (-40, -40)])}" fill="{HAIR_SH}"/>'
    bang_hi = f'<path d="{smooth([(-14, -80, 1), (0, -84), (16, -82, 1), (8, -79), (0, -76, 1), (-6, -80)])}" fill="{HAIR_HI}"/>'
    s.append(F.part(bangs, HAIR, HAIR_SH, ang, 5, bang_hi, sw=3.0, extra_shade=bang_sh))
    return ''.join(s)


# ------------------------------------------------------------------- the body
def torso(F, ang, breath=0.0):
    s = []
    body = smooth([(-46, -128), (-14, -152), (26, -152), (44, -138), (47, -112), (40, -86), (28, -56),
                   (31, -24), (34, 6), (-32, 8), (-34, -22), (-28, -58), (-40, -100)])
    emblem = smooth([(25, -116, 1), (34, -98), (29, -84, 1), (24, -93), (18, -84, 1), (15, -99)])
    abs_lines = (line('M4,-44 Q14,-41 27,-44', 1.6, SUIT_HI) + line('M16,-56 L16,-26', 1.4, SUIT_HI))
    det = (abs_lines + f'<path d="{emblem}" fill="{GOLD}" stroke="{INK}" stroke-width="2"/>'
           + line('M20,-96 L24,-106 L28,-96', 1.4, GOLD_SH))
    s.append(F.part(body, SUIT, SUIT_SH, ang, 9, det, sw=3.2, rim=SUIT_HI))
    # cropped crimson jacket, open front, cream + gold trim
    coat = smooth([(-50, -128), (-16, -154), (10, -152), (12, -120), (10, -96), (14, -64, 1),
                   (-32, -58, 1), (-32, -94), (-46, -106)])
    coat_det = (line('M-30,-65 Q-6,-71 14,-68', 6, TRIM, 'butt') + line('M-30,-62 Q-6,-68 14,-65', 2, GOLD, 'butt')
                + line('M10,-150 Q14,-110 12,-66', 6, TRIM, 'butt') + line('M13,-150 Q17,-110 15,-66', 2, GOLD, 'butt')
                + line('M-20,-122 Q-26,-100 -22,-82', 1.6, COAT_SH))
    s.append(F.part(coat, COAT, COAT_SH, ang, 10, coat_det, sw=3.0, rim='#ff7a7a'))
    far_panel = smooth([(32, -148), (46, -134), (48, -110), (42, -80), (38, -66, 1), (34, -72), (36, -110), (30, -138)])
    s.append(F.part(far_panel, COAT, COAT_SH, ang, 3, line('M34,-140 Q40,-108 36,-70', 4, TRIM, 'butt'), sw=2.6))
    return ''.join(s)


def belt(F, ang):
    b = smooth([(-34, -18), (32, -22), (35, -6), (-33, -2)])
    det = (f'<rect x="10" y="-23" width="16" height="20" rx="3" fill="{GOLD}" stroke="{INK}" stroke-width="2"/>'
           f'<rect x="14" y="-18" width="8" height="10" rx="1.5" fill="{GOLD_SH}"/>'
           f'<rect x="-30" y="-21" width="14" height="16" rx="2" fill="#5a3a2c" stroke="{INK}" stroke-width="1.8"/>')
    return F.part(b, '#2a2433', '#151220', ang, 4, det, sw=2.6)


def scarf_wrap(F, ang):
    d = smooth([(-22, -160), (6, -150), (30, -160), (38, -146), (30, -134), (4, -128), (-22, -134), (-28, -148)])
    det = line('M-16,-146 Q6,-138 30,-146', 1.6, SCARF_SH) + line('M-10,-136 Q8,-130 28,-138', 1.4, SCARF_SH)
    return F.part(d, SCARF, SCARF_SH, ang, 5, det, sw=3.0)


def scarf_tails(F, t, wind):
    """Two flowing tails in torso space, anchored behind the neck. t: phase 0..1."""
    out = []
    for k, (ln, ph, w0) in enumerate([(150, 0.0, 20), (122, 0.33, 16)]):
        pts = []
        x, y = -18 + k * 6, -148 + k * 4
        a = 98 + wind * 55 - k * 6          # deg: 90 = straight down, larger swings back
        for i in range(9):
            pts.append((x, y))
            f = i / 8
            wav = 22 * f * math.sin(2 * math.pi * (t + ph) - f * 4.2) * (0.35 + wind)
            seg = ln / 8
            a_i = a + wav + f * 18 * wind
            x += seg * math.cos(math.radians(a_i))
            y += seg * math.sin(math.radians(a_i))
        pts.append((x, y))
        d = taper(pts, w0, 8, w0 + 6)
        tip = pts[-1]
        fringe = ''.join(line(f'M{tip[0] + dx:.1f},{tip[1] - 4:.1f} l{-2:.1f},{12}', 2, SCARF_SH) for dx in (-4, 0, 4))
        out.append(F.part(d, SCARF if k == 0 else SCARF_SH, SCARF_SH if k == 0 else '#0d5c72', 0, 5, '', sw=3.0) + fringe)
    return ''.join(out[::-1])


def upper_arm(F, ang):
    d = smooth([(-24, -4), (-8, -22), (16, -16), (22, 4), (18, 50), (16, 86, 1), (-16, 86, 1), (-20, 40)])
    det = (line('M-18,78 H18', 9, TRIM, 'butt') + line('M-18,82 H18', 2, GOLD, 'butt')
           + line('M-6,20 Q-10,46 -6,64', 1.6, COAT_SH) + line('M-20,4 Q-2,-6 18,0', 2, COAT_SH))
    return F.part(d, COAT, COAT_SH, ang, 6, det, sw=3.0, rim='#ff7a7a')


def forearm(F, ang):
    d = smooth([(-13, -8), (13, -8), (12, 40), (11, 86, 1), (-11, 86, 1), (-13, 40)])
    glove = (f'<path d="M-20,46 H20 V100 H-20 Z" fill="{GLOVE}"/>'
             f'<path d="{smooth([(-12, 50, 1), (12, 50, 1), (10, 74), (0, 80), (-10, 74)])}" fill="{GOLD}" stroke="{INK}" stroke-width="1.8"/>'
             + line('M-20,47 H20', 2.4))
    return F.part(d, SUIT, SUIT_SH, ang, 5, glove, sw=3.0, rim=SUIT_HI)


def fist(F, ang):
    d = smooth([(-12, -4), (12, -4), (17, 10), (17, 28), (8, 37), (-6, 36), (-14, 26), (-14, 8)])
    det = (line('M2,13 Q10,12 17,15', 1.6, GLOVE_LN) + line('M2,21 Q10,20 17,23', 1.6, GLOVE_LN)
           + line('M2,29 Q9,28 15,31', 1.6, GLOVE_LN)
           + f'<path d="{smooth([(0, 4), (12, 6), (15, 14), (6, 16), (0, 12)])}" fill="{GLOVE}" stroke="{INK}" stroke-width="1.8"/>'
           + f'<path d="M-8,0 Q0,-2 6,2" stroke="{GLOVE_LN}" stroke-width="2" fill="none"/>')
    return F.part(d, GLOVE, GLOVE_SH, ang, 4, det, sw=2.8, rim=GLOVE_LN)


def thigh(F, ang):
    d = smooth([(18, -20), (24, 10), (22, 60), (16, 110), (15, 134, 1), (-15, 134, 1), (-18, 100),
                (-22, 50), (-24, 10), (-20, -20)])
    det = line('M-4,30 Q0,70 -4,108', 1.5, SUIT_SH) + line('M17,30 L20,92', 2, SUIT_HI)
    return F.part(d, SUIT, SUIT_SH, ang, 8, det, sw=3.0, rim=SUIT_HI)


def shin(F, ang):
    d = smooth([(-14, -8), (14, -8), (14, 40), (12, 80), (10, 124, 1), (-12, 124, 1), (-16, 80),
                (-20, 40), (-18, 14)])
    boot = (f'<path d="{smooth([(-30, 62, 1), (30, 56, 1), (30, 140, 1), (-30, 140, 1)])}" fill="{GLOVE}"/>'
            + line('M-30,63 L30,57', 3) + line('M-30,70 L30,64', 5, GOLD, 'butt')
            + line('M8,80 L6,118', 2, GLOVE_LN))
    s = F.part(d, SUIT, SUIT_SH, ang, 6, boot, sw=3.0, rim=SUIT_HI)
    pad = smooth([(-6, -12), (11, -12), (15, 2), (11, 16), (-4, 16), (-8, 2)])
    s += F.part(pad, GOLD, GOLD_SH, ang, 4, line('M-1,-6 L8,-6', 2, '#fff2b0'), sw=2.6)
    return s


def foot(F, ang):
    d = smooth([(-14, -12), (12, -12), (34, 0), (44, 8), (44, 18, 1), (-17, 18, 1), (-18, 2)])
    det = (f'<path d="M-30,11 H60 V30 H-30 Z" fill="{GOLD}"/>' + line('M-30,11 H60', 2.4)
           + line('M18,-4 Q30,0 36,6', 1.6, GLOVE_LN))
    return F.part(d, GLOVE, GLOVE_SH, ang, 5, det, sw=3.0, rim=GLOVE_LN)


# --------------------------------------------------------------------- posing
def leg_ik(hip, ankle, l1=132.0, l2=124.0):
    """Two-bone IK -> (thigh_deg, shin_deg_relative). Knee bends forward (+x)."""
    dx, dy = ankle[0] - hip[0], ankle[1] - hip[1]
    d = min(math.hypot(dx, dy), l1 + l2 - 0.01)
    a_to = math.atan2(dx, dy)  # angle from +y toward +x
    cos_k = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    k = math.acos(max(-1, min(1, cos_k)))
    thigh = a_to + k            # knee forward
    knee = (hip[0] + l1 * math.sin(thigh), hip[1] + l1 * math.cos(thigh))
    shin_abs = math.atan2(ankle[0] - knee[0], ankle[1] - knee[1])
    # convert "angle from +y toward +x" to SVG rotation (deg): rotate(θ) maps (0,1) to (-sinθ, cosθ)
    return -math.degrees(thigh), -math.degrees(shin_abs - thigh)


def render(pose, scale=1.0):
    """pose keys: px, py (pelvis), torso, head, sh_n, el_n, wr_n, sh_f, el_f, wr_f,
    ank_n, ank_f (world ankle pos), foot_n, foot_f (world deg), blink, wind, phase, hair_lag"""
    F = Frame()
    P = pose
    px, py, ta = P['px'], P['py'], P['torso']

    def to_world(local):
        v = rot(local, ta)
        return (px + v[0], py + v[1])

    def arm(sh, el, wr, shoulder):
        a1 = ta + sh
        a2 = a1 + el
        a3 = a2 + wr
        return g(tr(*shoulder, sh), upper_arm(F, a1),
                 g(tr(0, 86, el), forearm(F, a2), g(tr(0, 84, wr) + ' scale(.86)', fist(F, a3))))

    def leg(hip_local, ank, foot_world):
        hip = to_world(hip_local)
        th, kn = leg_ik(hip, ank)
        a1 = th
        a2 = th + kn
        return g(tr(*hip, th), thigh(F, a1),
                 g(tr(0, 132, kn), shin(F, a2), g(tr(0, 124, foot_world - a2), foot(F, foot_world))))

    hip_n, hip_f = (-12, 2), (14, -2)
    sh_n, sh_f = (-20, -132), (28, -138)
    tor = f'translate({px:.2f},{py:.2f}) rotate({ta:.2f})'
    neck = (8, -150)
    layers = [
        g(tor, scarf_tails(F, P['phase'], P['wind'])),
        '<g filter="url(#far)">' + g(tor, arm(P['sh_f'], P['el_f'], P['wr_f'], sh_f)),
        leg(hip_f, P['ank_f'], P['foot_f']) + '</g>',
        g(tor, torso(F, ta)),
        leg(hip_n, P['ank_n'], P['foot_n']),
        g(tor, belt(F, ta)),
        g(tor, g(tr(*neck, P['head']) + ' scale(1.06)', head(F, ta + P['head'], P['blink'], P['hair_lag']))),
        g(tor, scarf_wrap(F, ta)),
        g(tor, arm(P['sh_n'], P['el_n'], P['wr_n'], sh_n)),
    ]
    body = ''.join(layers)
    filt = ('<filter id="far"><feColorMatrix type="matrix" values=".78 0 0 0 0  0 .8 0 0 .01  0 0 .86 0 .03  0 0 0 1 0"/></filter>'
            '<filter id="ink" x="-10%" y="-10%" width="120%" height="120%">'
            '<feMorphology in="SourceAlpha" operator="dilate" radius="2.2" result="d"/>'
            f'<feFlood flood-color="{INK}"/><feComposite in2="d" operator="in" result="o"/>'
            '<feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{round(W * scale)}" height="{round(H * scale)}" viewBox="0 0 {W} {H}">'
            f'<defs>{filt}{"".join(F.defs)}</defs><g filter="url(#ink)">{body}</g></svg>')
