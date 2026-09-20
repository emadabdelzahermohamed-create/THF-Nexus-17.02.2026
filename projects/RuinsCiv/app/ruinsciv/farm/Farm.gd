extends Control

const SAVE_PATH := "user://ruinsciv_farm_v1.json"
const PLOT_COUNT := 12

var tool := "plant"
var coins := 20
var plots: Array[Dictionary] = []
var plot_buttons: Array[Button] = []
var coins_label: Label
var hint_label: Label
var grid: GridContainer
var growth_timer: Timer

func _ready() -> void:
    _load_state()
    _build_ui()
    _refresh_all()
    growth_timer = Timer.new()
    growth_timer.wait_time = 3.0
    growth_timer.timeout.connect(_on_growth_tick)
    add_child(growth_timer)
    growth_timer.start()

func _blank_plot() -> Dictionary:
    return {"stage": 0, "watered": false, "progress": 0}

func _load_state() -> void:
    plots.clear()
    if FileAccess.file_exists(SAVE_PATH):
        var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
        var data = JSON.parse_string(file.get_as_text())
        if data is Dictionary:
            coins = int(data.get("coins", 20))
            var raw_plots = data.get("plots", [])
            if raw_plots is Array:
                for item in raw_plots:
                    if item is Dictionary:
                        plots.append(item)
    while plots.size() < PLOT_COUNT:
        plots.append(_blank_plot())
    if plots.size() > PLOT_COUNT:
        plots.resize(PLOT_COUNT)

func _save_state() -> void:
    var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    file.store_string(JSON.stringify({"coins": coins, "plots": plots}))

func _build_ui() -> void:
    var bg := ColorRect.new()
    bg.color = Color(0.06, 0.10, 0.07, 1)
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(bg)

    var root_margin := MarginContainer.new()
    root_margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root_margin.add_theme_constant_override("margin_left", 24)
    root_margin.add_theme_constant_override("margin_top", 20)
    root_margin.add_theme_constant_override("margin_right", 24)
    root_margin.add_theme_constant_override("margin_bottom", 20)
    add_child(root_margin)

    var stack := VBoxContainer.new()
    stack.add_theme_constant_override("separation", 12)
    root_margin.add_child(stack)

    var title := Label.new()
    title.text = "RuinsCiv Farm"
    title.add_theme_font_size_override("font_size", 30)
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    stack.add_child(title)

    coins_label = Label.new()
    coins_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    stack.add_child(coins_label)

    var tools := HBoxContainer.new()
    tools.alignment = BoxContainer.ALIGNMENT_CENTER
    stack.add_child(tools)
    for entry in [["plant", "Plant"], ["water", "Water"], ["harvest", "Harvest"]]:
        var b := Button.new()
        b.text = entry[1]
        b.pressed.connect(func(): _select_tool(entry[0]))
        tools.add_child(b)

    hint_label = Label.new()
    hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    stack.add_child(hint_label)

    grid = GridContainer.new()
    grid.columns = 4
    grid.size_flags_vertical = Control.SIZE_EXPAND_FILL
    stack.add_child(grid)

    for i in PLOT_COUNT:
        var plot_button := Button.new()
        plot_button.custom_minimum_size = Vector2(150, 92)
        plot_button.pressed.connect(func(): _use_tool(i))
        plot_buttons.append(plot_button)
        grid.add_child(plot_button)

    var back := Button.new()
    back.text = "Back to RuinsCiv"
    back.pressed.connect(func(): get_tree().change_scene_to_file("res://ruinsciv/Hub.tscn"))
    stack.add_child(back)

func _select_tool(next_tool: String) -> void:
    tool = next_tool
    hint_label.text = "Selected tool: " + tool.capitalize()

func _use_tool(index: int) -> void:
    var p := plots[index]
    match tool:
        "plant":
            if int(p["stage"]) == 0 and coins >= 1:
                coins -= 1
                p = {"stage": 1, "watered": false, "progress": 0}
        "water":
            if int(p["stage"]) in [1, 2]:
                p["watered"] = true
        "harvest":
            if int(p["stage"]) == 3:
                coins += 5
                ThfBridge.claim_farm_reward(5, {
                    "plot": index,
                    "crop": "starter_crop",
                    "growth_progress": int(p.get("progress", 0))
                })
                p = _blank_plot()
    plots[index] = p
    _save_state()
    _refresh_all()

func _on_growth_tick() -> void:
    var changed := false
    for i in plots.size():
        var p := plots[i]
        if int(p["stage"]) in [1, 2] and bool(p.get("watered", false)):
            p["progress"] = int(p.get("progress", 0)) + 1
            p["stage"] = 2
            p["watered"] = false
            if int(p["progress"]) >= 3:
                p["stage"] = 3
            plots[i] = p
            changed = true
    if changed:
        _save_state()
        _refresh_all()

func _refresh_all() -> void:
    if coins_label == null:
        return
    coins_label.text = "Farm Coins: %d  •  THF rewards are server-validated" % coins
    hint_label.text = "Selected tool: " + tool.capitalize()
    for i in plot_buttons.size():
        var p := plots[i]
        var stage := int(p["stage"])
        var text := "Empty"
        if stage == 1:
            text = "Seeded"
        elif stage == 2:
            text = "Growing %d/3" % int(p.get("progress", 0))
        elif stage == 3:
            text = "Ready!"
        if bool(p.get("watered", false)):
            text += "\nWatered"
        plot_buttons[i].text = "Plot %02d\n%s" % [i + 1, text]
