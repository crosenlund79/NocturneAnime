class_name PlayerInput
extends Node
## Feeds Input Map actions into the parent Character. Each player slot has its own actions
## (<action_prefix>move_left / _right / _up / _down / jump / crouch, see Project Settings >
## Input Map), so several players can share one keyboard without interfering.

@export var action_prefix := "p1_"

@onready var character: Character = get_parent()
var _left: StringName
var _right: StringName
var _up: StringName
var _down: StringName
var _jump: StringName
var _crouch: StringName


func _ready() -> void:
	process_priority = -1  # read input before the character moves this frame
	_left = StringName(action_prefix + "move_left")
	_right = StringName(action_prefix + "move_right")
	_up = StringName(action_prefix + "move_up")
	_down = StringName(action_prefix + "move_down")
	_jump = StringName(action_prefix + "jump")
	_crouch = StringName(action_prefix + "crouch")
	for action in [_left, _right, _up, _down, _jump, _crouch]:
		if not InputMap.has_action(action):
			push_error("PlayerInput: missing Input Map action '%s'" % action)


func _process(_delta: float) -> void:
	character.move_input = Input.get_vector(_left, _right, _up, _down)
	character.crouch_input = Input.is_action_pressed(_crouch)
	if Input.is_action_just_pressed(_jump):
		character.jump()
