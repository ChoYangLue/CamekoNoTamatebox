#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""KASANE multiple-exposure plug-in for GIMP 3.x."""

import sys

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, GObject, GLib


PROCEDURE_NAME = "plug-in-kasane-multiple-exposure"
PLUGIN_BINARY = "kasane-multiple-exposure"
MAX_LAYERS = 5


MODE_LABELS = {
    "screen": "スクリーン — 明るく幻想的",
    "lighten": "比較（明）— 光跡・星空向け",
    "average": "平均 — 自然でなめらか",
    "multiply": "乗算 — 影と質感を強調",
}


def average_opacity(bottom_up_index):
    """Return the opacity that gives every layer an equal final contribution."""
    return 100.0 / bottom_up_index


def error_result(procedure, message):
    return procedure.new_return_values(
        Gimp.PDBStatusType.CALLING_ERROR,
        GLib.Error(message),
    )


def show_dialog(procedure, config):
    gi.require_version("GimpUi", "3.0")
    from gi.repository import GimpUi

    GimpUi.init(PLUGIN_BINARY)
    dialog = GimpUi.ProcedureDialog.new(procedure, config, "KASANE — 多重露光")
    dialog.fill(["blend-mode", "opacity", "hide-originals", "group-name"])
    accepted = dialog.run()
    dialog.destroy()
    return accepted


def create_composite(image, layers, blend_mode, opacity, hide_originals, group_name):
    """Create a non-destructive layer group containing the composite."""
    layer_modes = {
        "screen": Gimp.LayerMode.SCREEN,
        "lighten": Gimp.LayerMode.LIGHTEN_ONLY,
        "multiply": Gimp.LayerMode.MULTIPLY,
    }

    image.undo_group_start()
    try:
        group = Gimp.GroupLayer.new(image)
        group.set_name(group_name.strip() or "KASANE — 多重露光")
        image.insert_layer(group, None, 0)

        # GIMP supplies selected drawables in visual stack order (top to bottom).
        # Insert every copy at position 0 while processing bottom to top to retain
        # that visual ordering inside the new group.
        for bottom_up_index, source in enumerate(reversed(layers), start=1):
            copy = Gimp.Layer.new_from_drawable(source, image)
            copy.set_name(source.get_name())

            success, offset_x, offset_y = source.get_offsets()
            if success:
                copy.set_offsets(offset_x, offset_y)

            image.insert_layer(copy, group, 0)
            copy.set_visible(True)

            if bottom_up_index == 1:
                copy.set_mode(Gimp.LayerMode.NORMAL)
                copy.set_opacity(100.0)
            elif blend_mode == "average":
                copy.set_mode(Gimp.LayerMode.NORMAL)
                copy.set_opacity(average_opacity(bottom_up_index))
            else:
                copy.set_mode(layer_modes[blend_mode])
                copy.set_opacity(opacity)

        if hide_originals:
            for source in layers:
                source.set_visible(False)

        image.set_selected_layers([group])
        return group
    finally:
        image.undo_group_end()


def run(procedure, run_mode, image, drawables, config, _data):
    layers = list(drawables)

    if not 2 <= len(layers) <= MAX_LAYERS:
        return error_result(
            procedure,
            f"2〜{MAX_LAYERS}個のレイヤーを選択してください（現在: {len(layers)}個）。",
        )

    if any(not isinstance(layer, Gimp.Layer) for layer in layers):
        return error_result(procedure, "レイヤーだけを選択してください。")

    if run_mode == Gimp.RunMode.INTERACTIVE and not show_dialog(procedure, config):
        return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)

    blend_mode = config.get_property("blend-mode")
    opacity = config.get_property("opacity")
    hide_originals = config.get_property("hide-originals")
    group_name = config.get_property("group-name")

    if blend_mode not in MODE_LABELS:
        return error_result(procedure, f"未対応の合成方法です: {blend_mode}")

    try:
        create_composite(
            image,
            layers,
            blend_mode,
            opacity,
            hide_originals,
            group_name,
        )
        Gimp.displays_flush()
    except Exception as exc:  # GIMP reports this in its plug-in error dialog.
        return procedure.new_return_values(
            Gimp.PDBStatusType.EXECUTION_ERROR,
            GLib.Error(f"多重露光の作成に失敗しました: {exc}"),
        )

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


class KasanePlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        return [PROCEDURE_NAME]

    def do_create_procedure(self, name):
        if name != PROCEDURE_NAME:
            return None

        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            run,
            None,
        )
        procedure.set_image_types("RGB*, GRAY*")
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLES)
        procedure.set_menu_label("KASANE — 多重露光…")
        procedure.add_menu_path("<Image>/Filters/Combine")
        procedure.set_attribution("KASANE", "KASANE", "2026")
        procedure.set_documentation(
            "選択した2〜5個のレイヤーから多重露光を作成します。",
            "元レイヤーを保持したまま専用グループへ複製し、スクリーン、比較（明）、平均、乗算のいずれかで合成します。",
            None,
        )

        choices = Gimp.Choice.new()
        for index, (nick, label) in enumerate(MODE_LABELS.items()):
            choices.add(nick, index, label, None)
        procedure.add_choice_argument(
            "blend-mode",
            "重なり方",
            "写真の合成方法を選びます",
            choices,
            "screen",
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_double_argument(
            "opacity",
            "合成レイヤーの濃度",
            "平均以外の合成で、2枚目以降に適用する不透明度",
            10.0,
            100.0,
            100.0,
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_boolean_argument(
            "hide-originals",
            "元レイヤーを非表示にする",
            "作成後に選択元のレイヤーを非表示にします（削除はしません）",
            True,
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_string_argument(
            "group-name",
            "グループ名",
            "作成する多重露光グループの名前",
            "KASANE — 多重露光",
            GObject.ParamFlags.READWRITE,
        )
        return procedure


Gimp.main(KasanePlugin.__gtype__, sys.argv)
