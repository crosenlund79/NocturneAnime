@tool
class_name ResolvedSprite2D
extends Sprite2D
## A Sprite2D whose template texture is swapped for a hand-drawn replacement at runtime.
## Assign the template_*.png as the texture in the editor as usual.


func _ready() -> void:
	if Engine.is_editor_hint() or texture == null:
		return
	texture = SpriteResolver.load_texture(texture.resource_path, Vector2i(texture.get_size()))
