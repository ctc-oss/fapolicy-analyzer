# Copyright Concurrent Technologies Corporation 2022
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
from typing import Dict, List, Mapping, Sequence, Union

import gi

from fapolicy_analyzer.ui.ui_page import UIAction

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class ActionToolbar(Gtk.Toolbar):
    def __init__(self, actions: Dict[str, List[UIAction]] = {}, **kwargs):
        super().__init__(**kwargs)
        self.__btn_action_map: Dict[Gtk.ToolButton, UIAction] = {}
        self.rebuild_toolbar(actions)

    def __lookup_icon_name(self, icon_name: str) -> Union[str, None]:
        """
        Attempts to verify that the icon can be loaded from the icon theme.

        Returns: the icon_name if it can be loaded or None
        """
        size = Gtk.IconSize.LARGE_TOOLBAR
        fallback = "image-missing"
        try:
            info = Gtk.IconTheme.get_default().lookup_icon(icon_name, size, 0)
            info.load_icon()
            return icon_name
        except Exception as ex1:
            logging.warning(
                f"Unable to load image {icon_name} falling back to '{fallback}' icon."
            )
            logging.debug(ex1)
            try:
                info = Gtk.IconTheme.get_default().lookup_icon(fallback, size, 0)
                info.load_icon()
                return fallback
            except Exception as ex2:
                logging.warning(
                    f"Unable to load image '{fallback}' falling back to text only."
                )
                logging.debug(ex2)
                return None

    def remove_all_items(self):
        for btn in self.get_children():
            btn.destroy()
        self.__btn_action_map = {}

    def rebuild_toolbar(self, actions: Mapping[str, Sequence[UIAction]]):
        def create_button(action: UIAction) -> Gtk.ToolButton:
            btn = Gtk.ToolButton(
                label=action.name,
                tooltip_text=action.tooltip,
                sensitive=action.sensitivity_func(),
            )

            btn.set_icon_name(self.__lookup_icon_name(action.icon))

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
