class_name Location
extends Node2D
## A place characters can stand in. Describes the walkable floor; knows nothing about who walks it.

## Feet positions are kept inside this rectangle.
@export var walk_area := Rect2(80, 500, 1120, 200)
## Character scale at the back / front edge of walk_area.
@export var depth_scale := Vector2(0.88, 1.0)


func place(character: Character) -> void:
	character.walk_area = walk_area
	character.depth_scale = depth_scale
