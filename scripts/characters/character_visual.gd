@tool
class_name CharacterVisual
extends AnimatedSprite2D
## Builds the character's animations from its definition (through SpriteResolver, so hand-drawn
## replacements are picked up) and plays the right one for the current motion.

var _definition: CharacterDefinition
var _base_offset := Vector2.ZERO


func setup(definition: CharacterDefinition) -> void:
	_definition = definition
	if definition == null:
		sprite_frames = null
		return
	var size := definition.display_size()
	var frames := SpriteFrames.new()
	frames.remove_animation(&"default")
	for anim in definition.animations:
		frames.add_animation(anim.name)
		frames.set_animation_speed(anim.name, anim.fps)
		frames.set_animation_loop(anim.name, anim.loop)
		for i in anim.frame_count:
			frames.add_frame(anim.name, SpriteResolver.load_texture(definition.frame_template_path(anim, i), size))
	sprite_frames = frames
	centered = true
	_base_offset = (Vector2(definition.canvas_size) * 0.5 - definition.origin) * definition.display_scale
	_update_offset()
	play(definition.idle_animation)


## Picks the animation for the character's current state.
## jump_progress: 0..1 through the air; landing: true while the landing pose is held.
func show_state(direction: Vector2, crouching: bool, airborne: bool, jump_progress: float, landing: bool) -> void:
	if _definition == null:
		return
	if direction.x != 0.0:
		flip_h = direction.x < 0.0
		_update_offset()
	var d := _definition
	if (airborne or landing) and sprite_frames.has_animation(d.jump_animation):
		# key poses follow the jump arc instead of a frame rate, so pose and height always agree
		var count := sprite_frames.get_frame_count(d.jump_animation)
		var index := count - 1 if landing else clampi(int(jump_progress * (count - 1)), 0, count - 2)
		if animation != d.jump_animation:
			animation = d.jump_animation
		pause()
		frame = index
		return
	var moving := direction != Vector2.ZERO
	var target := d.walk_animation if moving else d.idle_animation
	if crouching:
		var crouch_target := d.crouch_walk_animation if moving else d.crouch_animation
		if sprite_frames.has_animation(crouch_target):
			target = crouch_target
	if animation != target or not is_playing():
		play(target)


func _update_offset() -> void:
	# keep the feet on the origin when mirrored
	offset = Vector2(-_base_offset.x if flip_h else _base_offset.x, _base_offset.y)


func _validate_property(property: Dictionary) -> void:
	# frames are rebuilt from the definition at load time; never bake them into scene files
	if property.name in ["sprite_frames", "animation", "offset", "flip_h"]:
		property.usage &= ~PROPERTY_USAGE_STORAGE
