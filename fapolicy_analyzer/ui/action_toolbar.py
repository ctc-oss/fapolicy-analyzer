from typing import Dict, Sequence

import gi
from fapolicy_analyzer.ui.ui_page import UIAction

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class ActionToolbar(Gtk.Toolbar):
    def __init__(self, actions: Dict[str, Sequence[UIAction]] = {}, **kwargs):
        super().__init__(**kwargs)
        self.__btn_action_map = {}
        self.rebuild_toolbar(actions)

    def remove_all_items(self):
        for btn in self.get_children():
            btn.destroy()
        self.__btn_action_map = {}

    def rebuild_toolbar(self, actions: Dict[str, Sequence[UIAction]]):
        def create_button(action: UIAction) -> Gtk.ToolButton:
            btn = Gtk.ToolButton(
                label=action.name,
                icon_name=action.icon,
                tooltip_text=action.tooltip,
                sensitive=action.sensitivity_func(),
            )
            for signal, handler in action.signals.items():
                btn.connect(signal, handler)
            self.__btn_action_map[btn] = action
            return btn

        self.remove_all_items()

        for idx, k in enumerate(actions.keys()):
            if idx > 0:
                self.insert(Gtk.SeparatorToolItem(), -1)
            for action in actions[k]:
                btn = create_button(action)
                self.insert(btn, -1)
        self.show_all()

    def refresh_buttons_sensitivity(self):
        for btn, action in self.__btn_action_map.items():
            btn.set_sensitive(action.sensitivity_func())
