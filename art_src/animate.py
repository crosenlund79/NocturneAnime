"""Pose the rig for every frame, rasterize with Chromium and pack sprite sheets + a Godot SpriteFrames resource.
usage: python3 animate.py <scratch_dir>"""
import math, os, subprocess, sys
from PIL import Image
from character import render, W, H, GROUND

SCALE = 0.75                     # frames are rasterized at their in-game size for crisp vector edges
WALK_N, WALK_FPS, IDLE_N, IDLE_FPS = 12, 14, 24, 12
STRIDE = 60                      # half step length (frame px)
ANK = GROUND - 18                # ankle height when the foot is flat
FAR_Y = -4                       # far foot sits slightly higher on screen (depth)
PX = 196
OUT = os.path.join(os.path.dirname(__file__), '..', 'art')


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

    fw, fh = round(W * SCALE), round(H * SCALE)
    for name, poses in jobs:
        n = len(poses)
        cols = min(n, 6)
        rows = math.ceil(n / cols)
        sheet = Image.new('RGBA', (fw * cols, fh * rows))
        for i in range(n):
            sheet.paste(Image.open(os.path.join(tmp, f'{name}_{i:02d}.png')), ((i % cols) * fw, (i // cols) * fh))
        sheet.save(os.path.join(OUT, f'hero_{name}.png'), optimize=True)
    Image.open(os.path.join(tmp, 'showcase.png')).save(os.path.join(OUT, 'hero_showcase.png'), optimize=True)

    # SpriteFrames resource
    subs, anims, k = [], [], 0
    for name, poses, fps in [(j[0], j[1], WALK_FPS if j[0] == 'walk' else IDLE_FPS) for j in jobs]:
        frames = []
        for i in range(len(poses)):
            k += 1
            x, y = (i % 6) * fw, (i // 6) * fh
            subs.append(f'[sub_resource type="AtlasTexture" id="a{k}"]\natlas = ExtResource("{name}")\nregion = Rect2({x}, {y}, {fw}, {fh})\n')
            frames.append(f'{{"duration": 1.0, "texture": SubResource("a{k}")}}')
        anims.append(f'{{"frames": [{", ".join(frames)}], "loop": true, "name": &"{name}", "speed": {float(fps)}}}')
    tres = (f'[gd_resource type="SpriteFrames" load_steps={k + 3} format=3]\n\n'
            '[ext_resource type="Texture2D" path="res://art/hero_idle.png" id="idle"]\n'
            '[ext_resource type="Texture2D" path="res://art/hero_walk.png" id="walk"]\n\n'
            + '\n'.join(subs) + f'\n[resource]\nanimations = [{", ".join(anims)}]\n')
    open(os.path.join(OUT, 'hero_frames.tres'), 'w').write(tres)
    print('frame', fw, fh, 'feet at', PX * SCALE, GROUND * SCALE,
          'walk speed px/s', 4 * STRIDE * SCALE / (WALK_N / WALK_FPS))


if __name__ == '__main__':
    main(sys.argv[1])
