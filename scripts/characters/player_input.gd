class_name PlayerInput
extends Node
## Feeds WASD / arrow-key input into the parent Character.

@onready var character: Character = get_parent()


func _ready() -> void:
	process_priority = -1  # read input before the character moves this frame


func _process(_delta: float) -> void:
	character.move_input = Input.get_vector(&"move_left", &"move_right", &"move_up", &"move_down")
