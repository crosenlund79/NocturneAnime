"""Dev helper: python3 preview.py <module> <out_dir>  -> idle + walk key poses on a flat background."""
import importlib, os, subprocess, sys
from PIL import Image
import rig
mod = importlib.import_module(sys.argv[1]); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
poses = [mod.idle(rig.idle_pose(.25, 0)), getattr(mod, 'walk', lambda p: p)(rig.walk_pose(0)), getattr(mod, 'walk', lambda p: p)(rig.walk_pose(.25))]
files = []
for i, P in enumerate(poses):
    f = os.path.join(out, f'{sys.argv[1]}_{i}.svg'); open(f, 'w').write(mod.render(P, 2.0)); files.append(f)
subprocess.run(['node', os.path.join(os.path.dirname(__file__), 'render.js'), out] + files, check=True)
ims = [Image.open(f[:-4] + '.png') for f in files]
sheet = Image.new('RGBA', (sum(i.width for i in ims), ims[0].height), (200, 215, 235, 255))
x = 0
for im in ims: sheet.alpha_composite(im, (x, 0)); x += im.width
sheet.save(os.path.join(out, f'{sys.argv[1]}_sheet.png'))
sheet.crop((150, 20, 650, 520)).save(os.path.join(out, f'{sys.argv[1]}_head.png'))
