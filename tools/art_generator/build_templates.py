"""Pose the rig for every frame and rasterize the artwork *templates* used by the game.

usage: python3 build_templates.py <scratch_dir>

Writes  assets/sprites/characters/hero/animations/<anim>/template_<anim>_NN.png
        assets/sprites/environments/rooftop/template_background.png
Only template_ files are ever written, so hand-drawn replacements are never touched.
Keep CANVAS / ORIGIN / fps in sync with resources/characters/hero/hero.tres."""
import math, os, subprocess, sys
from PIL import Image
from character import render, W, H, GROUND

SCALE = 1.5                      # template canvas = 2x the in-game size (600x960), comfortable to draw over
WALK_N, WALK_FPS, IDLE_N, IDLE_FPS = 12, 14, 24, 12
STRIDE = 60                      # half step length (frame px)
ANK = GROUND - 18                # ankle height when the foot is flat
FAR_Y = -4                       # far foot sits slightly higher on screen (depth)
PX = 196
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
HERO_DIR = os.path.join(ROOT, 'assets', 'sprites', 'characters', 'hero', 'animations')
BG_PATH = os.path.join(ROOT, 'assets', 'sprites', 'environments', 'rooftop', 'template_background.png')


def foot_ground(ang):
    """Ankle y that keeps the lowest of heel/toe on the ground for a foot rotated by ang deg."""
    a = math.radians(ang)
    toe = 44 * math.sin(a) + 18 * math.cos(a)
    heel = -17 * math.sin(a) + 18 * math.cos(a)
    return GROUND - max(toe, heel)


def ease(x):
    return x * x * (3 - 2 * x)


def leg_cycle(q, ground_off):
    """q in [0,1): 0 = heel strike, 0..0.5 stance, 0.5..1 swing. Returns ankle pos (rel x) and foot angle."""
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
        y = foot_ground(ang) - 34 * math.sin(math.pi * min(1, s * 1.15)) ** 1.2
    return x, y + ground_off, ang


def walk_pose(p):
    c = math.cos(2 * math.pi * p)
    bob = math.cos(4 * math.pi * p)
    xn, yn, an = leg_cycle(p, 0)
    xf, yf, af = leg_cycle(p + 0.5, FAR_Y)
    lag = p - 0.06
    sw = math.cos(2 * math.pi * lag)
    return dict(px=PX, py=341 + 4.5 * bob, torso=5 + 1.2 * math.cos(4 * math.pi * (p - 0.1)),
                head=-3 - 1.5 * math.cos(4 * math.pi * (p - 0.15)),
                sh_n=8 + 28 * sw, el_n=-14 - 26 * max(0, -sw), wr_n=4,
                sh_f=4 - 26 * sw, el_f=-14 - 26 * max(0, sw), wr_f=4,
                ank_n=(PX - 8 + xn, yn), ank_f=(PX + 18 + xf, yf), foot_n=an, foot_f=af,
                blink=0, wind=0.55 + 0.1 * bob, phase=p * 2, hair_lag=5 * math.sin(4 * math.pi * (p - 0.2)))


def idle_pose(t, i):
    b = math.sin(2 * math.pi * t)
    blink = {17: 0.55, 18: 1.0, 19: 0.45}.get(i, 0)
    return dict(px=PX, py=338 + 1.6 * b, torso=1.5 + 0.7 * b, head=-1 + 1.4 * math.sin(2 * math.pi * t - 0.7),
                sh_n=58 - 1.5 * b, el_n=-110 + 2 * b, wr_n=-24, sh_f=-8 + 2 * b, el_f=-18 - 2 * b, wr_f=4,
                ank_n=(164, ANK), ank_f=(236, ANK + FAR_Y), foot_n=0, foot_f=-3,
                blink=blink, wind=0.18 + 0.08 * math.sin(2 * math.pi * t), phase=t,
                hair_lag=1.5 * math.sin(2 * math.pi * t - 1.2))


def main(tmp):
    os.makedirs(tmp, exist_ok=True)
    jobs = [('walk', [walk_pose(i / WALK_N) for i in range(WALK_N)]),
            ('idle', [idle_pose(i / IDLE_N, i) for i in range(IDLE_N)])]
    files = []
    for name, poses in jobs:
        for i, P in enumerate(poses):
            f = os.path.join(tmp, f'{name}_{i:02d}.svg')
            open(f, 'w').write(render(P, SCALE))
            files.append(f)
    # hi-res showcase of the idle key pose
    f = os.path.join(tmp, 'showcase.svg')
    open(f, 'w').write(render(idle_pose(0.25, 0), 2.0))
    files.append(f)
    subprocess.run(['node', os.path.join(os.path.dirname(__file__), 'render.js'), tmp] + files, check=True)

    for name, poses in jobs:
        out_dir = os.path.join(HERO_DIR, name)
        os.makedirs(out_dir, exist_ok=True)
        for i in range(len(poses)):
            Image.open(os.path.join(tmp, f'{name}_{i:02d}.png')).save(
                os.path.join(out_dir, f'template_{name}_{i + 1:02d}.png'), optimize=True)
    Image.open(os.path.join(tmp, 'showcase.png')).save(os.path.join(ROOT, 'docs', 'images', 'hero_showcase.png'), optimize=True)

    here = os.path.dirname(__file__)
    bg_svg = os.path.join(tmp, 'template_background.svg')
    subprocess.run([sys.executable, os.path.join(here, 'background.py'), bg_svg], check=True)
    subprocess.run(['node', os.path.join(here, 'render.js'), os.path.dirname(BG_PATH), bg_svg], check=True)

    print('canvas', round(W * SCALE), round(H * SCALE), 'origin (feet)', PX * SCALE, GROUND * SCALE,
          'walk speed at display_scale 0.5:', 4 * STRIDE * SCALE * 0.5 / (WALK_N / WALK_FPS))


if __name__ == '__main__':
    main(sys.argv[1])
