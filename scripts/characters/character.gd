@tool
class_name Character
extends Node2D
## Moves a character from intents set by a controller (player input now, AI later):
## a direction, a held crouch and a jump request. Knows nothing about input devices or how the
## character is drawn.

@export var definition: CharacterDefinition:
	set(value):
		definition = value
		if is_node_ready():
			_apply_definition()

## Desired movement direction, length 0..1. Written by a controller node.
var move_input := Vector2.ZERO
## True while the controller wants to crouch. Ignored in the air.
var crouch_input := false
## Area the feet must stay inside; an empty rect means unbounded. Set by the location.
var walk_area := Rect2()
## Scale at the top / bottom of walk_area, for a simple depth effect.
var depth_scale := Vector2.ONE

## Height of the feet above the ground in screen px (the position itself stays on the ground).
var height := 0.0
var _air_time := -1.0  # < 0: on the ground
var _landing := 0.0

@onready var visual: CharacterVisual = $Visual
@onready var shadow: CharacterShadow = $Shadow


func _ready() -> void:
	_apply_definition()


## Starts a jump if standing on the ground (no double jumps).
func jump() -> void:
	if definition and not is_airborne():
		_air_time = 0.0


func is_airborne() -> bool:
	return _air_time >= 0.0


func is_crouching() -> bool:
	return crouch_input and not is_airborne()


func _process(delta: float) -> void:
	if Engine.is_editor_hint() or definition == null:
		return
	var speed := definition.crouch_speed if is_crouching() else definition.walk_speed
	position += Vector2(move_input.x * speed, move_input.y * definition.depth_speed) * delta
	if walk_area.has_area():
		position = position.clamp(walk_area.position, walk_area.end)
		var depth := inverse_lerp(walk_area.position.y, walk_area.end.y, position.y)
		scale = Vector2.ONE * lerpf(depth_scale.x, depth_scale.y, depth)

	var progress := 0.0
	if is_airborne():
		_air_time += delta
		progress = minf(_air_time / definition.jump_duration, 1.0)
		height = definition.jump_height * 4.0 * progress * (1.0 - progress)  # parabola
		if progress >= 1.0:
			_air_time = -1.0
			height = 0.0
			_landing = definition.landing_time
	else:
		_landing = maxf(_landing - delta, 0.0)

	visual.position.y = -height
	shadow.set_lift(height / definition.jump_height)
	visual.show_state(move_input, is_crouching(), is_airborne(), progress, _landing > 0.0)


func _apply_definition() -> void:
	visual.setup(definition)
	if definition:
		shadow.radius = definition.shadow_radius
