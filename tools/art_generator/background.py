"""Simple anime-style backdrop: cel-shaded sky, clouds, layered skyline and a tiled plaza. -> background.svg"""
import random, sys
from character import smooth

random.seed(7)
W, H, HORIZON = 1280, 720, 455


def cloud(x, y, s):
    """White puffs with a flat base; shading = the puffs minus a copy nudged toward the sun."""
    puffs = [(-1.25, -.05, .42), (-.7, -.35, .55), (-.05, -.55, .68), (.6, -.38, .58), (1.15, -.08, .45)]

    def circles(ox, oy):
        return ''.join(f'<circle cx="{x + dx * s + ox:.0f}" cy="{y + dy * s + oy:.0f}" r="{r * s:.0f}"/>'
                       for dx, dy, r in puffs)
    cid = f'cl{x}'
    return (f'<clipPath id="{cid}"><rect x="{x - 3 * s}" y="{y - 3 * s}" width="{6 * s}" height="{3 * s}"/></clipPath>'
            f'<clipPath id="{cid}b">{circles(0, 0)}</clipPath>'
            f'<g clip-path="url(#{cid})"><g clip-path="url(#{cid}b)"><rect x="{x - 3 * s}" y="{y - 3 * s}" '
            f'width="{6 * s}" height="{3 * s}" fill="#cfdffb"/><g fill="#ffffff">{circles(-.08 * s, -.2 * s)}</g></g></g>')


def skyline(base, hmin, hmax, wmin, wmax, fill, win=None):
    x, out = -20, []
    while x < W + 20:
        w = random.randint(wmin, wmax)
        h = random.randint(hmin, hmax)
        out.append(f'<rect x="{x}" y="{base - h}" width="{w}" height="{h + 2}" fill="{fill}"/>')
        if random.random() < .25:
            out.append(f'<rect x="{x + w * .4:.0f}" y="{base - h - 18}" width="3" height="18" fill="{fill}"/>')
        if win:
            for wy in range(base - h + 12, base - 10, 16):
                for wx in range(x + 6, x + w - 8, 12):
                    if random.random() < .5:
                        out.append(f'<rect x="{wx}" y="{wy}" width="5" height="7" fill="{win}"/>')
        x += w + random.randint(0, 6)
    return ''.join(out)


tiles = []
for i in range(-14, 15):  # perspective lines toward a vanishing point
    tiles.append(f'<line x1="{640 + i * 22}" y1="{HORIZON}" x2="{640 + i * 260}" y2="{H}" stroke="#b9b3cf" stroke-width="2"/>')
y, step = HORIZON + 8, 10
while y < H:
    tiles.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" stroke="#b9b3cf" stroke-width="2"/>')
    step *= 1.32
    y += step

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#3f8cf0"/><stop offset=".55" stop-color="#8cc4ff"/><stop offset="1" stop-color="#d9efff"/></linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dcd8ea"/><stop offset="1" stop-color="#ece8f2"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<path d="M0,180 L1280,40 L1280,64 L0,214 Z" fill="#ffffff" opacity=".12"/>
<path d="M0,250 L1280,120 L1280,132 L0,266 Z" fill="#ffffff" opacity=".10"/>
{cloud(230, 140, 70)}{cloud(980, 125, 95)}{cloud(700, 250, 45)}{cloud(1180, 300, 40)}
{skyline(HORIZON - 30, 60, 210, 40, 90, "#a9bfe8", "#c3d4f2")}
{skyline(HORIZON, 30, 120, 50, 120, "#8299cc", "#9db1db")}
<rect x="0" y="{HORIZON - 26}" width="{W}" height="26" fill="#6f7fb0"/>
<rect x="0" y="{HORIZON - 26}" width="{W}" height="5" fill="#8f9dcc"/>
<g stroke="#3d4570" stroke-width="3">{''.join(f'<line x1="{x}" y1="{HORIZON - 70}" x2="{x}" y2="{HORIZON - 26}"/>' for x in range(10, W, 64))}</g>
<rect x="0" y="{HORIZON - 74}" width="{W}" height="6" fill="#3d4570"/>
<rect x="0" y="{HORIZON - 50}" width="{W}" height="3" fill="#3d4570"/>
<rect x="0" y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="url(#floor)"/>
{''.join(tiles)}
<rect x="0" y="{HORIZON}" width="{W}" height="6" fill="#9a93b8"/>
<path d="M0,{H - 70} Q640,{H - 110} 1280,{H - 70} L1280,{H} L0,{H} Z" fill="#ffffff" opacity=".18"/>
</svg>'''
open(sys.argv[1], 'w').write(svg)
