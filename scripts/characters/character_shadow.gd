@tool
class_name CharacterShadow
extends Node2D
## Soft ground shadow under a character's feet.

@export var radius := 70.0:
	set(value):
		radius = value
		queue_redraw()
@export var color := Color(0.25, 0.2, 0.4, 0.28)


func _draw() -> void:
	draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0, 0.22))
	draw_circle(Vector2.ZERO, radius, color)
