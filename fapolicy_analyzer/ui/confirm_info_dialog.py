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

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .configs import Colors
from .strings import (
    CHANGESET_ACTION_ADD,
    CHANGESET_ACTION_DEL,
    DEPLOY_ANCILLARY_CONFIRM_DIALOG_TEXT,
    DEPLOY_ANCILLARY_CONFIRM_DIALOG_TITLE,
    DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR,
    DEPLOY_ANCILLARY_CONFIRM_DLG_PATH_COL_HDR,
)


class ConfirmInfoDialog(Gtk.Dialog):
    def __init__(self, parent=None, listPathActionPairs=[]):
        Gtk.Dialog.__init__(
            self,
            title=DEPLOY_ANCILLARY_CONFIRM_DIALOG_TITLE,
            transient_for=parent,
            flags=0,
        )

        self._bSaveStatePreDeploy = False
        self._btnCbSaveState = None

        self.add_buttons(
            Gtk.STOCK_NO, Gtk.ResponseType.NO, Gtk.STOCK_YES, Gtk.ResponseType.YES
        )

        self.set_default_size(-1, 200)

        changeStore = Gtk.ListStore(str, str)
        self.__load_path_action_list(changeStore, listPathActionPairs)
        tree_view = Gtk.TreeView(model=changeStore)
        tree_view.get_selection().set_mode(Gtk.SelectionMode.NONE)

        columnAction = Gtk.TreeViewColumn(
            DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR,
            Gtk.CellRendererText(background=Colors.LIGHT_GRAY),
            text=0,
        )
        columnAction.set_sort_column_id(0)
        tree_view.append_column(columnAction)

        columnFile = Gtk.TreeViewColumn(
            DEPLOY_ANCILLARY_CONFIRM_DLG_PATH_COL_HDR, Gtk.CellRendererText(), text=1
        )
        columnFile.set_sort_column_id(1)
        tree_view.append_column(columnFile)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(tree_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)

        box = self.get_content_area()
        box.add(Gtk.Label(label=DEPLOY_ANCILLARY_CONFIRM_DIALOG_TEXT))

        box.pack_start(scrolled_window, True, True, 0)
        self._btnCbSaveState = Gtk.CheckButton(
            label='"Save As..." fapolicyd data and configuration to archive prior to deployment.'
        )
        frameCb = Gtk.Frame()
        frameCb.add(self._btnCbSaveState)
        box.add(frameCb)

        self.show_all()

    def get_save_state(self):
        return self._bSaveStatePreDeploy

    def __load_path_action_list(self, store, listPathActionPairs):
        if listPathActionPairs:
            for e in listPathActionPairs:
                # tuples are in (path,action) order, displayed as (action,path)
                action = (
                    CHANGESET_ACTION_ADD
                    if e[-1] == "Add"
                    else CHANGESET_ACTION_DEL
                    if e[-1] == "Del"
                    else ""
                )
                store.append((action, e[0]))

    def run(self):
        response = super().run()
        self._bSaveStatePreDeploy = self._btnCbSaveState.get_active()
        return response
