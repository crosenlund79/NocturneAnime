@tool
class_name SpriteAnimation
extends Resource
## One full-body animation. Frames live in
## <sprite_dir>/animations/<name>/template_<name>_01.png, _02.png, ...

@export var name: StringName
@export_range(1, 999) var frame_count := 1
@export var fps := 12.0
@export var loop := true
