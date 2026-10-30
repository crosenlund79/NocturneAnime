"""Shared 2D cut-out rig used by every character.

Body parts are hand-placed spline shapes in their own bone space. A pose (joint angles + world
ankle targets) becomes one SVG frame. Cel shading is generated per part by subtracting a copy of
the shape shifted toward a fixed world light, so the shadow side stays put while limbs rotate;
a dilated-silhouette filter adds the heavier outer ink line. Character modules (atlas.py,
fishcat.py) supply the drawings and layer order; this module supplies everything they share.
"""
import math

W, H = 400, 640          # frame size in px (templates are rendered at 1.5x)
GROUND = 612             # y of the ground line in the frame
PX = 196                 # x of the pelvis / feet
INK = '#1c1424'
LIGHT = (0.55, -0.83)    # world-space direction *toward* the key light (upper front)
THIGH, SHIN = 132.0, 124.0
HIP_N, HIP_F = (-12, 2), (14, -2)          # hip joints in torso space (near / far leg)
SH_N, SH_F = (-20, -132), (28, -138)       # shoulder joints in torso space
NECK = (8, -150)


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



def streaks(x, y, ang=-20, n=4, length=14, gap=4.0, w=1.6, c='#d6f6ff'):
    """Atlas's signature light streaks: a short bundle of parallel highlight strokes."""
    out = ''
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nx, ny = -dy, dx
    for i in range(n):
        o = (i - (n - 1) / 2) * gap
        L = length * (1 - abs(i - (n - 1) / 2) / n * 0.6)
        cx, cy = x + nx * o, y + ny * o
        out += line(f'M{cx - dx * L / 2:.1f},{cy - dy * L / 2:.1f} L{cx + dx * L / 2:.1f},{cy + dy * L / 2:.1f}', w, c)
    return out


def blobs(pts, fill, r=(4, 3)):
    """Irregular spots (Fishcat's markings)."""
    out = ''
    for i, (x, y, s) in enumerate(pts):
        k = [(1, 0), (.6, .8), (-.5, .9), (-1, .1), (-.6, -.8), (.5, -.9)]
        p = [(x + r[0] * s * a * (1 + .18 * math.sin(i * 7 + j)), y + r[1] * s * b * (1 + .18 * math.cos(i * 5 + j)))
             for j, (a, b) in enumerate(k)]
        out += f'<path d="{smooth(p)}" fill="{fill}"/>'
    return out


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



def foot_ground(ang, toe=44, heel=17, sole=18):
    """Ankle y that keeps the lowest of heel/toe on the ground for a foot rotated by ang deg."""
    a = math.radians(ang)
    return GROUND - max(toe * math.sin(a) + sole * math.cos(a), -heel * math.sin(a) + sole * math.cos(a))


def to_world(P, local):
    v = rot(local, P['torso'])
    return (P['px'] + v[0], P['py'] + v[1])


def arm_chain(P, side, upper, fore, hand, upper_len=86, fore_len=84, hand_scale=.86):
    """Shoulder -> elbow -> wrist group in torso space. upper/fore/hand: f(abs_angle) -> svg."""
    sh, el, wr = P['sh_' + side], P['el_' + side], P['wr_' + side]
    a1 = P['torso'] + sh
    a2, a3 = a1 + el, a1 + el + wr
    joint = SH_N if side == 'n' else SH_F
    return g(tr(*joint, sh), upper(a1),
             g(tr(0, upper_len, el), fore(a2), g(tr(0, fore_len, wr) + f' scale({hand_scale})', hand(a3))))


def leg_chain(P, side, thigh, shin, foot):
    """Hip -> knee -> ankle -> foot in world space via 2-bone IK toward P['ank_<side>']."""
    hip = to_world(P, HIP_N if side == 'n' else HIP_F)
    th, kn = leg_ik(hip, P['ank_' + side], THIGH, SHIN)
    fa = P['foot_' + side]
    # shin + foot first, thigh on top: the rounded thigh end hides the knee joint
    return g(tr(*hip, th), g(tr(0, THIGH, kn), shin(th + kn), g(tr(0, SHIN, fa - th - kn), foot(fa))),
             thigh(th))


def knee_world(P, side):
    hip = to_world(P, HIP_N if side == 'n' else HIP_F)
    th, _ = leg_ik(hip, P['ank_' + side], THIGH, SHIN)
    return (hip[0] - THIGH * math.sin(math.radians(th)), hip[1] + THIGH * math.cos(math.radians(th)))


def torso_group(P, *items):
    return f'<g transform="translate({P["px"]:.2f},{P["py"]:.2f}) rotate({P["torso"]:.2f})">' + ''.join(items) + '</g>'


def far(*items):
    """Far-side limbs: slightly darker/cooler so depth reads."""
    return '<g filter="url(#far)">' + ''.join(items) + '</g>'


def document(F, body, scale=1.0, char_scale=1.0):
    """Wrap layers into the final SVG with the far-tint and outer-ink filters.
    char_scale shrinks the whole character about the feet (for shorter characters)."""
    filt = ('<filter id="far"><feColorMatrix type="matrix" values=".8 0 0 0 0  0 .82 0 0 .01  0 0 .88 0 .03  0 0 0 1 0"/></filter>'
            '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>'
            '<filter id="ink" x="-10%" y="-10%" width="120%" height="120%">'
            '<feMorphology in="SourceAlpha" operator="dilate" radius="2.2" result="d"/>'
            f'<feFlood flood-color="{INK}"/><feComposite in2="d" operator="in" result="o"/>'
            '<feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    cs = f'translate({PX},{GROUND}) scale({char_scale}) translate({-PX},{-GROUND})'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{round(W * scale)}" height="{round(H * scale)}" viewBox="0 0 {W} {H}">'
            f'<defs>{filt}{"".join(F.defs)}</defs><g filter="url(#ink)"><g transform="{cs}">{body}</g></g></svg>')


# --------------------------------------------------------------------- motion
STRIDE = 60                      # half step length (frame px)
FAR_Y = -4                       # far foot sits slightly higher on screen (depth)


def ease(x):
    return x * x * (3 - 2 * x)


def leg_cycle(q, ground_off, lift=34):
    """q in [0,1): 0 = heel strike, 0..0.5 stance, 0.5..1 swing -> (rel x, ankle y, foot angle)."""
    q %= 1.0
    if q < 0.5:
        s = q / 0.5
        x = STRIDE - 2 * STRIDE * s
        ang = -14 * max(0, 1 - s / 0.18) + 26 * max(0, (s - 0.62) / 0.38) ** 1.5
        y = foot_ground(ang)
    else:
        s = (q - 0.5) / 0.5
        x = -STRIDE + 2 * STRIDE * ease(s)
        ang = 26 * (1 - s) ** 2 - 14 * ease(max(0, (s - 0.55) / 0.45))
        y = foot_ground(ang) - lift * math.sin(math.pi * min(1, s * 1.15)) ** 1.2
    return x, y + ground_off, ang


def walk_pose(p, arm_swing=28, lift=34):
    bob = math.cos(4 * math.pi * p)
    xn, yn, an = leg_cycle(p, 0, lift)
    xf, yf, af = leg_cycle(p + 0.5, FAR_Y, lift)
    sw = math.cos(2 * math.pi * (p - 0.06))
    return dict(px=PX, py=341 + 4.5 * bob, torso=5 + 1.2 * math.cos(4 * math.pi * (p - 0.1)),
                head=-3 - 1.5 * math.cos(4 * math.pi * (p - 0.15)),
                sh_n=8 + arm_swing * sw, el_n=-14 - 26 * max(0, -sw), wr_n=4,
                sh_f=4 - arm_swing * 0.93 * sw, el_f=-14 - 26 * max(0, sw), wr_f=4,
                ank_n=(PX - 8 + xn, yn), ank_f=(PX + 18 + xf, yf), foot_n=an, foot_f=af,
                blink=0, wind=0.55 + 0.1 * bob, phase=p * 2, cycle=p, moving=1.0,
                hair_lag=5 * math.sin(4 * math.pi * (p - 0.2)))


def idle_pose(t, i, blink_frames=(17, 18, 19)):
    b = math.sin(2 * math.pi * t)
    blink = dict(zip(blink_frames, (0.55, 1.0, 0.45))).get(i, 0)
    return dict(px=PX, py=338 + 1.6 * b, torso=1.5 + 0.7 * b, head=-1 + 1.4 * math.sin(2 * math.pi * t - 0.7),
                sh_n=12 - 2 * b, el_n=-16 - 2 * b, wr_n=2, sh_f=-8 + 2 * b, el_f=-18 - 2 * b, wr_f=2,
                ank_n=(166, GROUND - 18), ank_f=(232, GROUND - 18 + FAR_Y), foot_n=0, foot_f=-3,
                blink=blink, wind=0.18 + 0.08 * math.sin(2 * math.pi * t), phase=t, cycle=t, moving=0.0,
                breath=b, hair_lag=1.5 * math.sin(2 * math.pi * t - 1.2))
