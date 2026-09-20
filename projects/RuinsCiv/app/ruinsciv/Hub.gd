extends Control

@onready var status_label: Label = $Center/Panel/Margin/Stack/ThfStatus

func _ready() -> void:
    $Center/Panel/Margin/Stack/City.pressed.connect(_open_city)
    $Center/Panel/Margin/Stack/Farm.pressed.connect(_open_farm)
    $Center/Panel/Margin/Stack/Refresh.pressed.connect(_refresh_status)
    _refresh_status()

func _open_city() -> void:
    get_tree().change_scene_to_file("res://scenes/boot/Boot.tscn")

func _open_farm() -> void:
    get_tree().change_scene_to_file("res://ruinsciv/farm/Farm.tscn")

func _refresh_status() -> void:
    status_label.text = ThfBridge.get_status()
