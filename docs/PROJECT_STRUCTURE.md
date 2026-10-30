# Project structure

Godot 4.3, GDScript, GL Compatibility renderer. Main scene: `scenes/main/main.tscn`.

```
assets/        Raw artwork, audio and fonts, grouped by kind and then by owner
  sprites/characters/<id>/animations/<anim>/   full-body animation frames (template_ + replacements)
  sprites/environments/<location>/              backgrounds
  sprites/objects/, sprites/ui/                 (empty, reserved)
  audio/music|sfx|ambience/, fonts/            (empty, reserved)
scenes/        Reusable .tscn files
  main/         entry scene: puts characters into a location
  characters/   character.tscn (generic) + one small inherited scene per character (hero.tscn)
  environments/ one scene per location (rooftop.tscn)
  ui/           (reserved)
scripts/       GDScript, mirroring scenes/ plus shared systems
  characters/   Character (movement), CharacterVisual (animation playback), PlayerInput,
                CharacterDefinition + SpriteAnimation (data resources), CharacterShadow
  environments/ Location (walk area, depth scale)
  systems/      SpriteResolver (template -> replacement lookup), ResolvedSprite2D
  main/, ui/
resources/     Data (.tres): characters/<id>/<id>.tres, configurations/ for future game-wide settings
autoload/      Reserved for singletons; currently none and none are needed
docs/          This documentation (ignored by Godot via .gdignore)
tools/         Offline art generator that produced the template_ images (ignored by Godot)
```

## How the pieces fit

| Responsibility | Where |
|---|---|
| Identity, artwork layout, animation list, speeds | `resources/characters/hero/hero.tres` (`CharacterDefinition`) |
| Animation frames | `assets/sprites/characters/hero/animations/<anim>/` |
| Template → replacement lookup | `scripts/systems/sprite_resolver.gd` (one static helper, used by everything) |
| Visual playback (frames, facing, idle/walk choice) | `CharacterVisual` (the `Visual` node) |
| Movement, bounds, depth scale | `Character` (root of `character.tscn`) |
| Input | `PlayerInput` node, added as a child of the character in `main.tscn` |
| Walkable area of a place | `Location` (root of each environment scene) |

`Character` only reads a `move_input` vector; it doesn't know about the keyboard. A future NPC gets
an AI controller node that writes `move_input` instead of `PlayerInput`.

## Adding things

- **New character:** create `assets/sprites/characters/<id>/animations/...` frames, a
  `resources/characters/<id>/<id>.tres` (`CharacterDefinition`) and a two-line inherited scene
  `scenes/characters/<id>.tscn` from `character.tscn` that assigns the definition. No code changes.
- **New animation state:** add frames under `animations/<name>/` and a `SpriteAnimation` entry in the
  definition. Choosing *when* to play it (beyond idle/walk) goes in `CharacterVisual.show_motion`.
- **New location:** `scenes/environments/<name>.tscn` with a `Location` root and a `ResolvedSprite2D`
  background whose texture is a `template_*.png` under `assets/sprites/environments/<name>/`.
- **Objects / UI / audio:** use the reserved folders; any `Sprite2D` that should accept hand-drawn
  replacements uses the `ResolvedSprite2D` script.

## Conventions

- snake_case files and folders; PascalCase `class_name`s and node names.
- Character-specific files live only in folders named after the character id.
- Tunable values live in exported properties / `.tres`, not in code.
- Generated artwork is always named `template_*`; nothing ever writes a file without that prefix.
- No autoloads or managers until something actually needs global state.
