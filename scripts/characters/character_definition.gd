@tool
class_name CharacterDefinition
extends Resource
## Identity, artwork layout and movement tuning of one character. Add a character by creating a
## new .tres of this type plus its sprite folder; no scripts or scenes need copying.

@export var id: StringName
@export var display_name := ""

@export_group("Artwork")
## Root of this character's artwork, e.g. res://assets/sprites/characters/hero
@export_dir var sprite_dir := ""
## Size of every template frame in pixels. All frames share this canvas.
@export var canvas_size := Vector2i(600, 960)
## Point between the feet on the canvas; it is placed on the character's position.
@export var origin := Vector2(300, 918)
## Canvas pixels -> screen pixels.
@export var display_scale := 0.5
@export var animations: Array[SpriteAnimation] = []
@export var idle_animation: StringName = &"idle"
@export var walk_animation: StringName = &"walk"

@export_group("Movement")
## Horizontal speed in px/s; matches the stride drawn in the walk cycle so feet don't slide.
@export var walk_speed := 210.0
## Speed toward / away from the camera in px/s.
@export var depth_speed := 130.0
@export var shadow_radius := 70.0


func frame_template_path(animation: SpriteAnimation, index: int) -> String:
	return sprite_dir.path_join("animations/%s/template_%s_%02d.png" % [animation.name, animation.name, index + 1])


func display_size() -> Vector2i:
	return Vector2i((Vector2(canvas_size) * display_scale).round())
