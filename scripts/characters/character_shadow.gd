@tool
class_name CharacterShadow
extends Node2D
## Soft ground shadow under a character's feet; shrinks and fades as the character rises.

@export var radius := 70.0:
	set(value):
		radius = value
		queue_redraw()
@export var color := Color(0.25, 0.2, 0.4, 0.28)


## lift: 0 on the ground .. 1 at the top of a jump.
func set_lift(lift: float) -> void:
	scale = Vector2.ONE * lerpf(1.0, 0.6, lift)
	modulate.a = lerpf(1.0, 0.5, lift)


func _draw() -> void:
	draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0, 0.22))
	draw_circle(Vector2.ZERO, radius, color)
