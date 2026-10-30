extends Node2D
## Moves the hero on the plaza floor and switches between idle / walk.

const WALK_SPEED := 210.0   # matches the stride baked into the walk cycle, so feet don't slide
const DEPTH_SPEED := 130.0
const FLOOR_TOP := 500.0
const FLOOR_BOTTOM := 700.0

@onready var sprite: AnimatedSprite2D = $Sprite


func _ready() -> void:
	sprite.play("idle")


func _process(delta: float) -> void:
	var dir := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	position += Vector2(dir.x * WALK_SPEED, dir.y * DEPTH_SPEED) * delta
	position.x = clampf(position.x, 80.0, 1200.0)
	position.y = clampf(position.y, FLOOR_TOP, FLOOR_BOTTOM)
	# a touch of depth: further away = slightly smaller
	scale = Vector2.ONE * lerpf(0.88, 1.0, inverse_lerp(FLOOR_TOP, FLOOR_BOTTOM, position.y))

	if dir.x != 0.0:
		sprite.flip_h = dir.x < 0.0
	sprite.play("walk" if dir != Vector2.ZERO else "idle")
