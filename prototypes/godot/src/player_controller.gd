class_name PlayerController
extends CharacterBody3D

signal exit_reached(edge_id: int)

@export var speed := 5.5
@export var mouse_sensitivity := 0.0025
var camera: Camera3D


func _ready() -> void:
	camera = Camera3D.new()
	camera.position = Vector3(0.0, 0.65, 0.0)
	add_child(camera)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		camera.rotation.x = clampf(camera.rotation.x - event.relative.y * mouse_sensitivity, -1.35, 1.35)
	if event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED else Input.MOUSE_MODE_CAPTURED


func _physics_process(_delta: float) -> void:
	var input_vector := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var move_direction := (transform.basis * Vector3(input_vector.x, 0.0, input_vector.y)).normalized()
	velocity.x = move_direction.x * speed
	velocity.z = move_direction.z * speed
	if not is_on_floor():
		velocity.y -= 20.0 * get_physics_process_delta_time()
	else:
		velocity.y = 0.0
	move_and_slide()


func reset_to_center() -> void:
	position = Vector3(0.0, 1.0, 2.5)
	velocity = Vector3.ZERO
