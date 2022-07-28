# Copyright Concurrent Technologies Corporation 2021
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

from locale import gettext as _
from typing import Sequence, Tuple

import gi
from fapolicy_analyzer import System, rules_difference
from fapolicy_analyzer.ui.changeset_wrapper import Changeset, TrustChangeset
from fapolicy_analyzer.ui.configs import Colors
from fapolicy_analyzer.ui.strings import (
    CHANGESET_ACTION_ADD_TRUST,
    CHANGESET_ACTION_DEL_TRUST,
    CHANGESET_ACTION_RULES,
    DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR,
    DEPLOY_ANCILLARY_CONFIRM_DLG_CHANGE_COL_HDR,
)
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk  # isort: skip


class ConfirmDeploymentDialog(UIBuilderWidget):
    def __init__(
        self,
        changesets: Sequence[Changeset],
        current_system: System,
        previous_system: System,
        parent: Gtk.Window = None,
    ):
        super().__init__()

        if parent:
            self.get_ref().set_transient_for(parent)

        changes_view = self.get_object("changesTreeView")
        self.__config_changes_view(changes_view)
        store = self.__load_store(changesets, current_system, previous_system)
        changes_view.set_model(store)

    def __config_changes_view(self, view: Gtk.TreeView):
        columnAction = Gtk.TreeViewColumn(
            DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR,
            Gtk.CellRendererText(background=Colors.LIGHT_GRAY),
            text=0,
        )
        columnAction.set_sort_column_id(0)
        view.append_column(columnAction)

        columnFile = Gtk.TreeViewColumn(
            DEPLOY_ANCILLARY_CONFIRM_DLG_CHANGE_COL_HDR, Gtk.CellRendererText(), text=1
        )
        columnFile.set_sort_column_id(1)
        view.append_column(columnFile)

    def __to_path_action_pairs(
        self,
        changesets: Sequence[Changeset],
        current_system: System,
        previous_system: System,
    ) -> Sequence[Tuple[str, str]]:
        def rules_changes():
            if not previous_system or not current_system:
                return []
            diffs = rules_difference(previous_system, current_system).split("\n")
            adds = len([d for d in diffs if d.startswith("+")])
            dels = len([d for d in diffs if d.startswith("-")])
            if (adds + dels) == 0:
                return []

            add_text = f"{adds} addition{'s' if adds > 1 else ''}" if adds else None
            del_text = f"{dels} removal{'s' if dels > 1 else ''}" if dels else None
            message = " and ".join((m for m in [add_text, del_text] if m)) + " made"
            return [(_(message), "Rules")]

        def trust_changes():
            return [
                t
                for e in changesets
                if isinstance(e, TrustChangeset)
                for t in e.serialize().items()
            ]

        return [*trust_changes(), *rules_changes()]

    def __load_store(
        self,
        changesets: Sequence[Changeset],
        current_system: System,
        previous_system: System,
    ) -> Gtk.ListStore:
        action_txt = {
            "Add": CHANGESET_ACTION_ADD_TRUST,
            "Del": CHANGESET_ACTION_DEL_TRUST,
            "Rules": CHANGESET_ACTION_RULES,
        }
        store = Gtk.ListStore(str, str)
        pathActionPairs = self.__to_path_action_pairs(
            changesets, current_system, previous_system
        )
        for e in pathActionPairs:
            # tuples are in (path,action) order, displayed as |action|path|
            action = action_txt.get(e[-1], "")
            store.append((action, e[0]))
        return store

    def get_save_state(self) -> bool:
        return self.get_object("saveStateCbn").get_active()
