@tool
class_name Character
extends Node2D
## Moves a character from a direction set by a controller (player input now, AI later).
## Knows nothing about input devices or how the character is drawn.

@export var definition: CharacterDefinition:
	set(value):
		definition = value
		if is_node_ready():
			_apply_definition()

## Desired movement direction, length 0..1. Written by a controller node.
var move_input := Vector2.ZERO
## Area the feet must stay inside; an empty rect means unbounded. Set by the location.
var walk_area := Rect2()
## Scale at the top / bottom of walk_area, for a simple depth effect.
var depth_scale := Vector2.ONE

@onready var visual: CharacterVisual = $Visual
@onready var shadow: CharacterShadow = $Shadow


func _ready() -> void:
	_apply_definition()


func _process(delta: float) -> void:
	if Engine.is_editor_hint() or definition == null:
		return
	position += Vector2(move_input.x * definition.walk_speed, move_input.y * definition.depth_speed) * delta
	if walk_area.has_area():
		position = position.clamp(walk_area.position, walk_area.end)
		var depth := inverse_lerp(walk_area.position.y, walk_area.end.y, position.y)
		scale = Vector2.ONE * lerpf(depth_scale.x, depth_scale.y, depth)
	visual.show_motion(move_input)


func _apply_definition() -> void:
	visual.setup(definition)
	if definition:
		shadow.radius = definition.shadow_radius
