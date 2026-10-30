@tool
class_name SpriteResolver
extends RefCounted
## Resolves artwork templates to hand-drawn replacements.
##
## For a template "<dir>/template_<name>.png" the first existing file wins:
##   1. <folder of the executable>/<dir without res://>/<name>.png|.jpg|.jpeg  (exported builds only)
##   2. <dir>/<name>.png|.jpg|.jpeg                                          (project folder)
##   3. the template itself
## Every frame / image is resolved independently, so artwork can be replaced piece by piece.

const TEMPLATE_PREFIX := "template_"
const EXTENSIONS: PackedStringArray = ["png", "jpg", "jpeg", "PNG", "JPG", "JPEG"]


## Returns the texture for a template, preferring a replacement. If `size` is given, the image is
## scaled to it (Lanczos), so replacements may be drawn on a larger canvas of the same proportions.
static func load_texture(template_path: String, size := Vector2i.ZERO) -> Texture2D:
	var path := resolve_path(template_path)
	var image := _load_image(path)
	if image == null:
		push_error("SpriteResolver: cannot load '%s'" % path)
		return null
	if size != Vector2i.ZERO and image.get_size() != size:
		var ratio := float(image.get_width()) / image.get_height()
		if absf(ratio - float(size.x) / size.y) > 0.01:
			push_warning("SpriteResolver: '%s' is %s, expected the template proportions %s" % [path, image.get_size(), size])
		image.resize(size.x, size.y, Image.INTERPOLATE_LANCZOS)
	return ImageTexture.create_from_image(image)


## Path of the image that will actually be used for `template_path`.
static func resolve_path(template_path: String) -> String:
	var file := template_path.get_file()
	if not file.begins_with(TEMPLATE_PREFIX):
		return template_path
	var stem := file.get_basename().trim_prefix(TEMPLATE_PREFIX)
	for dir in _search_dirs(template_path.get_base_dir()):
		for ext in EXTENSIONS:
			var candidate := dir.path_join("%s.%s" % [stem, ext])
			if _exists(candidate):
				return candidate
	return template_path


## Folder beside the executable that mirrors res:// for user artwork in exported builds.
static func external_root() -> String:
	return OS.get_executable_path().get_base_dir()


static func _search_dirs(template_dir: String) -> PackedStringArray:
	var dirs := PackedStringArray()
	if not OS.has_feature("editor") and template_dir.begins_with("res://"):
		dirs.append(external_root().path_join(template_dir.trim_prefix("res://")))
	dirs.append(template_dir)
	return dirs


static func _exists(path: String) -> bool:
	if path.begins_with("res://") and not OS.has_feature("editor"):
		return ResourceLoader.exists(path)  # exported: only imported images are packed
	return FileAccess.file_exists(path)


static func _load_image(path: String) -> Image:
	if path.begins_with("res://") and not OS.has_feature("editor"):
		var texture := load(path) as Texture2D
		return texture.get_image() if texture else null
	# Editor runs and external files: read straight from disk, so a freshly saved drawing
	# works before (or without) the editor importing it.
	var image := Image.load_from_file(ProjectSettings.globalize_path(path))
	if image and image.is_compressed():
		image.decompress()
	return image
