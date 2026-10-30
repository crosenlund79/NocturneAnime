# Sprite drawing guide

Every image the game shows starts as a generated **template** (`template_*.png`). Saving a drawing
with the same name minus `template_` replaces it automatically. Templates are never modified.

## Workflow

1. Open `assets/sprites/characters/hero/animations/walk/` (or `idle/`).
2. Open e.g. `template_walk_03.png` in your drawing app (Krita, Clip Studio, Procreate, Photoshop…).
3. Draw your version on a new layer above it, then hide/delete the template layer.
4. Save as `walk_03.png` **in the same folder**. Keep the template file.
5. Run the game (F5). Frame 3 of the walk now uses your drawing; every other frame keeps its template.

Replace frames one at a time, in any order. Delete your file to go back to the template.

## Naming

| Template | Your replacement |
|---|---|
| `template_walk_03.png` | `walk_03.png` (or `.jpg` / `.jpeg`) |
| `template_idle_12.png` | `idle_12.png` |
| `environments/rooftop/template_background.png` | `environments/rooftop/background.png` |

If both a PNG and a JPG exist, the PNG is used. Frame numbers are 2 digits, starting at `01`.

## Canvas, alignment and transparency

- **Character frames: 600 × 960 px, transparent background.** The game shows them at half size.
- You may draw on a larger canvas with the **same proportions** (1200 × 1920, 2400 × 3840); it is scaled
  down automatically. Always scale the template up first so everything stays aligned.
- **Don't crop or move the canvas.** The point between the feet on the ground is at **x 294, y 918**;
  that point is pinned to the character's position. Keep the feet on that ground line in every frame,
  or the character will appear to slide or bob.
- Draw the character facing **right**; the game mirrors it when walking left.
- Use **PNG with transparency** for characters. JPG has no transparency, so a JPG frame shows its white
  background. JPG is fine for backgrounds.
- Background: 1280 × 720.
- Timing is fixed per animation (idle 24 frames @ 12 fps, walk 12 frames @ 14 fps, see
  `resources/characters/hero/hero.tres`). Keep the same pose order as the templates.
- The ground shadow is drawn by the game; don't paint one into the frames.

## Exported Windows builds

Drawings saved in the project folder before exporting are packed into the game automatically.

To add or change artwork **after** exporting, create the same folder path next to the `.exe`:

```
MyGame.exe
assets/sprites/characters/hero/animations/walk/walk_03.png
assets/sprites/environments/rooftop/background.png
```

Files there win over anything packed inside the game. Restart the game to see changes.

## Regenerating templates

`tools/art_generator/` contains the code that drew the templates (Python + Pillow, Node + Playwright):
`python3 tools/art_generator/build_templates.py <temp folder>`. It only writes `template_*` files, so
your drawings are safe.
