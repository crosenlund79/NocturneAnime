"""Pose every character's rig for every frame and rasterize the artwork *templates* the game uses.

usage: python3 build_templates.py <scratch_dir> [character ...]

Writes  assets/sprites/characters/<id>/animations/<anim>/template_<anim>_NN.png
        assets/sprites/environments/rooftop/template_background.png   (when no character is named)
Only template_ files are ever written, so hand-drawn replacements are never touched.
Keep canvas / origin / fps / walk_speed in sync with resources/characters/<id>/<id>.tres."""
import importlib, os, subprocess, sys
from PIL import Image
import rig

SCALE = 1.5                      # template canvas = 2x the in-game size (600x960), comfortable to draw over
ANIMS = {'idle': (24, 12), 'walk': (12, 14)}   # frames, fps
CHARACTERS = ['atlas', 'fishcat']
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BG_PATH = os.path.join(ROOT, 'assets', 'sprites', 'environments', 'rooftop', 'template_background.png')


def poses(mod, anim):
    n = ANIMS[anim][0]
    if anim == 'idle':
        return [mod.idle(rig.idle_pose(i / n, i)) for i in range(n)]
    walk = getattr(mod, 'walk', lambda p: p)
    return [walk(rig.walk_pose(i / n)) for i in range(n)]


def main(tmp, names):
    os.makedirs(tmp, exist_ok=True)
    files, jobs = [], []
    for name in names:
        mod = importlib.import_module(name)
        for anim in ANIMS:
            for i, P in enumerate(poses(mod, anim)):
                f = os.path.join(tmp, f'{name}__{anim}_{i + 1:02d}.svg')
                open(f, 'w').write(mod.render(P, SCALE))
                files.append(f)
                jobs.append((name, anim, i))
        f = os.path.join(tmp, f'{name}__showcase.svg')
        open(f, 'w').write(mod.render(mod.idle(rig.idle_pose(.25, 0)), 2.0))
        files.append(f)
    subprocess.run(['node', os.path.join(HERE, 'render.js'), tmp] + files, check=True)

    for name, anim, i in jobs:
        out_dir = os.path.join(ROOT, 'assets', 'sprites', 'characters', name, 'animations', anim)
        os.makedirs(out_dir, exist_ok=True)
        Image.open(os.path.join(tmp, f'{name}__{anim}_{i + 1:02d}.png')).save(
            os.path.join(out_dir, f'template_{anim}_{i + 1:02d}.png'), optimize=True)
    for name in names:
        Image.open(os.path.join(tmp, f'{name}__showcase.png')).save(
            os.path.join(ROOT, 'docs', 'images', f'{name}_showcase.png'), optimize=True)
        cs = importlib.import_module(name).CHAR_SCALE
        print(f'{name}: canvas {round(rig.W * SCALE)}x{round(rig.H * SCALE)}, origin {rig.PX * SCALE},{rig.GROUND * SCALE},'
              f' walk_speed {4 * rig.STRIDE * SCALE * 0.5 * cs / (ANIMS["walk"][0] / ANIMS["walk"][1]):.1f}')

    if names == CHARACTERS:
        bg_svg = os.path.join(tmp, 'template_background.svg')
        subprocess.run([sys.executable, os.path.join(HERE, 'background.py'), bg_svg], check=True)
        subprocess.run(['node', os.path.join(HERE, 'render.js'), os.path.dirname(BG_PATH), bg_svg], check=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:] or CHARACTERS)
