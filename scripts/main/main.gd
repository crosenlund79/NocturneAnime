extends Node2D
## Entry scene: puts the characters into the current location.

@onready var location: Location = $Location


func _ready() -> void:
	for child in get_children():
		if child is Character:
			location.place(child)
