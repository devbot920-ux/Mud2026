extends Node

const WorldLoaderScript = preload("res://src/world_loader.gd")
const PlayerControllerScript = preload("res://src/player_controller.gd")
const ExitPortalScript = preload("res://src/exit_portal.gd")

const PORTAL_POSITIONS := {
	"N": [Vector3(0, 1.5, -8.8), 0.0], "NE": [Vector3(6.2, 1.5, -6.2), -PI / 4.0],
	"E": [Vector3(8.8, 1.5, 0), -PI / 2.0], "SE": [Vector3(6.2, 1.5, 6.2), -3.0 * PI / 4.0],
	"S": [Vector3(0, 1.5, 8.8), PI], "SW": [Vector3(-6.2, 1.5, 6.2), 3.0 * PI / 4.0],
	"W": [Vector3(-8.8, 1.5, 0), PI / 2.0], "NW": [Vector3(-6.2, 1.5, -6.2), PI / 4.0],
	"U": [Vector3(3.0, 1.5, -3.0), 0.0], "D": [Vector3(-3.0, 1.5, 3.0), PI],
}
const COMMAND_DIRECTIONS := {
	"n": "N", "north": "N", "ne": "NE", "northeast": "NE", "e": "E", "east": "E",
	"se": "SE", "southeast": "SE", "s": "S", "south": "S", "sw": "SW", "southwest": "SW",
	"w": "W", "west": "W", "nw": "NW", "northwest": "NW", "u": "U", "up": "U", "d": "D", "down": "D",
}

var world: Dictionary
var room_by_id: Dictionary = {}
var edge_by_id: Dictionary = {}
var outgoing_by_room: Dictionary = {}
var entity_by_type: Dictionary = {"npc": {}, "item": {}}
var spawn_by_room: Dictionary = {}
var current_room_id := -1
var show_hidden := false
var chamber: Node3D
var player: Variant
var title_label: Label
var description_label: RichTextLabel
var exit_box: VBoxContainer
var command_line: LineEdit
var dev_label: Label
var message_label: Label


func _ready() -> void:
	_configure_inputs()
	var result: Dictionary = WorldLoaderScript.load_fixture(WorldLoaderScript.fixture_path_from_arguments())
	if not result.ok:
		_show_fatal("Fixture validation failed:\n%s" % "\n".join(result.errors))
		return
	world = result.world
	_index_world()
	_build_environment()
	_build_ui()
	var primary: Array = world.fixture.primary_room_ids
	_enter_room(int(primary[0]))


func _configure_inputs() -> void:
	for pair: Array in [["move_forward", KEY_W], ["move_back", KEY_S], ["move_left", KEY_A], ["move_right", KEY_D]]:
		if not InputMap.has_action(pair[0]):
			InputMap.add_action(pair[0])
		var event := InputEventKey.new()
		event.physical_keycode = pair[1]
		InputMap.action_add_event(pair[0], event)


func _index_world() -> void:
	for room: Dictionary in world.rooms:
		room_by_id[room.id] = room
	for edge: Dictionary in world.edges:
		edge_by_id[edge.id] = edge
		if not outgoing_by_room.has(edge.from_room):
			outgoing_by_room[edge.from_room] = []
		outgoing_by_room[edge.from_room].append(edge)
	for npc: Dictionary in world.npcs:
		entity_by_type.npc[npc.id] = npc
	for item: Dictionary in world.items:
		entity_by_type.item[item.id] = item
	for spawn: Dictionary in world.spawns:
		spawn_by_room[spawn.id] = spawn


func _build_environment() -> void:
	chamber = Node3D.new()
	chamber.name = "RoomStage"
	add_child(chamber)
	var environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.025, 0.035, 0.055)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.55, 0.60, 0.70)
	env.ambient_light_energy = 0.55
	environment.environment = env
	add_child(environment)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55, -35, 0)
	light.light_energy = 1.2
	add_child(light)
	_add_static_box("Floor", Vector3(20, 0.3, 20), Vector3(0, -0.15, 0), Color(0.17, 0.19, 0.22))
	for wall: Array in [[Vector3(20, 4, 0.3), Vector3(0, 2, -10)], [Vector3(20, 4, 0.3), Vector3(0, 2, 10)], [Vector3(0.3, 4, 20), Vector3(-10, 2, 0)], [Vector3(0.3, 4, 20), Vector3(10, 2, 0)]]:
		_add_static_box("Wall", wall[0], wall[1], Color(0.11, 0.13, 0.16))
	player = PlayerControllerScript.new()
	player.name = "Player"
	var player_shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.4
	capsule.height = 1.8
	player_shape.shape = capsule
	player.add_child(player_shape)
	player.collision_layer = 1
	player.collision_mask = 1
	add_child(player)
	player.reset_to_center()


func _add_static_box(node_name: String, size: Vector3, at: Vector3, color: Color) -> void:
	var body := StaticBody3D.new()
	body.name = node_name
	body.position = at
	var collision := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = size
	collision.shape = shape
	body.add_child(collision)
	var instance := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	instance.mesh = mesh
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	instance.material_override = material
	body.add_child(instance)
	chamber.add_child(body)


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 22)
	margin.add_theme_constant_override("margin_top", 18)
	margin.add_theme_constant_override("margin_right", 22)
	margin.add_theme_constant_override("margin_bottom", 18)
	layer.add_child(margin)
	var root := HBoxContainer.new()
	margin.add_child(root)
	var info := VBoxContainer.new()
	info.custom_minimum_size = Vector2(440, 0)
	root.add_child(info)
	title_label = Label.new()
	title_label.add_theme_font_size_override("font_size", 25)
	info.add_child(title_label)
	description_label = RichTextLabel.new()
	description_label.fit_content = true
	description_label.custom_minimum_size = Vector2(430, 120)
	description_label.bbcode_enabled = true
	info.add_child(description_label)
	message_label = Label.new()
	message_label.modulate = Color(0.85, 0.82, 0.58)
	info.add_child(message_label)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(spacer)
	var sidebar := VBoxContainer.new()
	sidebar.custom_minimum_size = Vector2(310, 0)
	root.add_child(sidebar)
	var exit_heading := Label.new()
	exit_heading.text = "EXITS"
	sidebar.add_child(exit_heading)
	exit_box = VBoxContainer.new()
	sidebar.add_child(exit_box)
	var hidden_button := CheckButton.new()
	hidden_button.text = "Reveal hidden exits"
	hidden_button.toggled.connect(func(enabled: bool) -> void: show_hidden = enabled; _render_room())
	sidebar.add_child(hidden_button)
	dev_label = Label.new()
	dev_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dev_label.modulate = Color(0.62, 0.80, 0.88)
	sidebar.add_child(dev_label)
	var command_bar := VBoxContainer.new()
	command_bar.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	command_bar.offset_left = 22
	command_bar.offset_right = -22
	command_bar.offset_bottom = -18
	command_bar.offset_top = -84
	layer.add_child(command_bar)
	var help := Label.new()
	help.text = "WASD + mouse • Esc releases mouse • commands: n, sw, u, d, look"
	command_bar.add_child(help)
	command_line = LineEdit.new()
	command_line.placeholder_text = "Enter a MUD command…"
	command_line.text_submitted.connect(_on_command_submitted)
	command_bar.add_child(command_line)


func _enter_room(room_id: int) -> void:
	if not room_by_id.has(room_id):
		return
	current_room_id = room_id
	player.reset_to_center()
	_render_room()


func _render_room() -> void:
	for child: Node in chamber.get_children():
		if child.name.begins_with("Portal") or child.name.begins_with("Entity"):
			child.queue_free()
	var room: Dictionary = room_by_id[current_room_id]
	var title := str(WorldLoaderScript.field_value(room, "short_description", "Room %d" % current_room_id))
	var description := str(WorldLoaderScript.field_value(room, "long_description", "Boundary room stub."))
	title_label.text = title
	description_label.text = description
	message_label.text = ""
	for child: Node in exit_box.get_children():
		child.queue_free()
	var exits: Array = outgoing_by_room.get(current_room_id, [])
	var direction_slots: Dictionary = {}
	for edge: Dictionary in exits:
		if edge.hidden and not show_hidden:
			continue
		var direction: String = edge.direction
		var slot := int(direction_slots.get(direction, 0))
		direction_slots[direction] = slot + 1
		_add_exit(edge, slot)
	_spawn_entities()
	var classification: String = room.get("display", {}).get("classification", "unknown")
	dev_label.text = "DEV\nroom=%d  stable=%s\nscope=%s  class=%s\nsource_row=%s\nshort confidence=%s\noutgoing records=%d" % [current_room_id, room.get("stable_id", "?"), room.get("scope", "?"), classification, str(room.get("provenance", {}).get("source_row_id", "?")), WorldLoaderScript.field_confidence(room, "short_description"), exits.size()]


func _add_exit(edge: Dictionary, same_direction_index: int) -> void:
	var direction: String = edge.direction
	var arrangement: Array = PORTAL_POSITIONS.get(direction, [Vector3.ZERO, 0.0])
	var location: Vector3 = arrangement[0]
	var facing: float = arrangement[1]
	if same_direction_index > 0:
		location += Vector3(0.0, 0.0, float(same_direction_index) * 1.6)
	var portal: Variant = ExitPortalScript.new()
	portal.name = "Portal_%d" % int(edge.id)
	var destination: Dictionary = room_by_id[edge.to_room]
	var is_stub: bool = destination.get("scope", "") == "stub"
	var tint := Color(0.60, 0.25, 0.72) if edge.hidden else (Color(0.82, 0.55, 0.18) if edge.door else (Color(0.28, 0.55, 0.70) if is_stub else Color(0.35, 0.72, 0.56)))
	portal.configure(edge, location, facing, tint)
	portal.entered.connect(_on_exit_reached)
	chamber.add_child(portal)
	var button := Button.new()
	var markers: Array[String] = []
	if edge.door: markers.append("door")
	if edge.hidden: markers.append("hidden")
	if is_stub: markers.append("boundary")
	var suffix := " [%s]" % ", ".join(markers) if not markers.is_empty() else ""
	button.text = "%s → %d%s  (edge %d)" % [direction, int(edge.to_room), suffix, int(edge.id)]
	button.pressed.connect(func() -> void: _travel_edge(int(edge.id)))
	exit_box.add_child(button)


func _spawn_entities() -> void:
	if not spawn_by_room.has(current_room_id):
		return
	var spawn: Dictionary = spawn_by_room[current_room_id]
	var index := 0
	for entry: Dictionary in spawn.entries:
		var entity_type: String = entry.entity_type
		var entity: Dictionary = entity_by_type.get(entity_type, {}).get(entry.entity_id, {})
		for count_index: int in range(int(entry.count)):
			var marker := MeshInstance3D.new()
			marker.name = "Entity_%s_%d_%d" % [entity_type, int(entry.entity_id), count_index]
			var mesh: PrimitiveMesh = CapsuleMesh.new() if entity_type == "npc" else BoxMesh.new()
			if mesh is CapsuleMesh:
				mesh.height = 1.6
				mesh.radius = 0.45
			else:
				mesh.size = Vector3(0.55, 0.55, 0.55)
			marker.mesh = mesh
			marker.position = Vector3(-3.5 + float(index % 5) * 1.5, 0.8 if entity_type == "npc" else 0.3, -2.0 + float(index / 5) * 1.5)
			var material := StandardMaterial3D.new()
			material.albedo_color = Color(0.75, 0.24, 0.22) if entity_type == "npc" else Color(0.84, 0.72, 0.20)
			marker.material_override = material
			var label := Label3D.new()
			label.text = str(WorldLoaderScript.field_value(entity, "short_description", "%s %d" % [entity_type, int(entry.entity_id)]))
			label.position = Vector3(0, 1.2 if entity_type == "npc" else 0.65, 0)
			label.font_size = 24
			label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
			marker.add_child(label)
			chamber.add_child(marker)
			index += 1


func _on_exit_reached(edge_id: int) -> void:
	_travel_edge(edge_id)


func _travel_edge(edge_id: int) -> void:
	if not edge_by_id.has(edge_id):
		return
	var edge: Dictionary = edge_by_id[edge_id]
	if edge.from_room != current_room_id:
		return
	_enter_room(int(edge.to_room))


func _on_command_submitted(command: String) -> void:
	var normalized := command.strip_edges().to_lower()
	command_line.clear()
	if normalized == "look" or normalized == "l":
		_render_room()
		command_line.grab_focus()
		return
	if not COMMAND_DIRECTIONS.has(normalized):
		message_label.text = "Unknown command: %s" % normalized
		command_line.grab_focus()
		return
	var direction: String = COMMAND_DIRECTIONS[normalized]
	var matches: Array = []
	for edge: Dictionary in outgoing_by_room.get(current_room_id, []):
		if edge.direction == direction and (not edge.hidden or show_hidden):
			matches.append(edge)
	if matches.is_empty():
		message_label.text = "You cannot go %s." % direction
	elif matches.size() > 1:
		message_label.text = "%d parallel %s exits exist; use the exit list." % [matches.size(), direction]
	else:
		_travel_edge(int(matches[0].id))
	command_line.grab_focus()


func _show_fatal(message: String) -> void:
	push_error(message)
	var label := Label.new()
	label.text = message
	label.position = Vector2(30, 30)
	label.add_theme_color_override("font_color", Color(1.0, 0.35, 0.3))
	add_child(label)
