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

import fapolicy_analyzer.ui.strings as strings
import gi
from fapolicy_analyzer import Changeset
from more_itertools import first_true

from .actions import apply_changesets
from .add_file_button import AddFileButton
from .configs import Colors
from .confirm_change_dialog import ConfirmChangeDialog
from .searchable_list import SearchableList
from .store import dispatch
from .strings import FILE_LABEL, FILES_LABEL
from .trust_reconciliation_dialog import TrustReconciliationDialog

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # isort: skip

_UNTRUST_RESP = 0
_TRUST_RESP = 1


class SubjectList(SearchableList):
    def __init__(self):
        self.__events__ = [
            *super().__events__,
            "file_selection_changed",
        ]

        add_button = AddFileButton()
        add_button.files_added += lambda files: print(files)
        add_button.get_ref().set_sensitive(False)  # disable for now in readonly-view

        super().__init__(
            self._columns(),
            add_button.get_ref(),
            searchColumnIndex=2,
            defaultSortIndex=2,
            selection_type="multi",
        )

        self._systemTrust = []
        self._ancillaryTrust = []
        self.reconcileContextMenu = self.__build_reconcile_context_menu()
        self.fileChangeContextMenu = self.__build_change_trust_context_menu()
        self.load_store([])
        self.selection_changed += self.__handle_selection_changed
        self.get_object("treeView").connect("row-activated", self.on_view_row_activated)
        self.get_object("treeView").connect(
            "button-press-event", self.on_view_button_press_event
        )
        self.selection = []

    def __build_reconcile_context_menu(self):
        menu = Gtk.Menu()
        reconcileItem = Gtk.MenuItem.new_with_label("Reconcile File")
        reconcileItem.connect("activate", self.on_reconcile_file_activate)
        menu.append(reconcileItem)
        menu.show_all()
        return menu

    def __build_change_trust_context_menu(self):
        menu = Gtk.Menu()
        menu.trustItem = Gtk.MenuItem.new_with_label("Trust Files")
        menu.untrustItem = Gtk.MenuItem.new_with_label("Untrust Files")
        menu.trustItem.connect("activate", self.on_change_file_trust_activate)
        menu.untrustItem.connect("activate", self.on_change_file_trust_activate)
        menu.append(menu.trustItem)
        menu.append(menu.untrustItem)
        menu.show_all()
        return menu

    def _columns(self):
        def txt_color_func(col, renderer, model, iter, *args):
            color = model.get_value(iter, 5)
            renderer.set_property("foreground", color)

        trustCell = Gtk.CellRendererText(background=Colors.LIGHT_GRAY, xalign=0.5)
        trustColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_TRUST_HEADER, trustCell, markup=0
        )
        trustColumn.set_sort_column_id(0)
        accessCell = Gtk.CellRendererText(background=Colors.LIGHT_GRAY, xalign=0.5)
        accessColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_ACCESS_HEADER, accessCell, markup=1
        )
        accessColumn.set_sort_column_id(1)
        fileRenderer = Gtk.CellRendererText()
        fileColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_FILE_HEADER,
            fileRenderer,
            text=2,
            cell_background=4,
        )
        fileColumn.set_cell_data_func(fileRenderer, txt_color_func)
        fileColumn.set_sort_column_id(2)
        return [trustColumn, accessColumn, fileColumn]

    def _trust_markup(self, subject):

        status = subject.trust_status.lower()
        trust = subject.trust.lower()
        if not status == "t":
            at_str = (
                f'<span color="{Colors.RED}"><b>AT</b></span>'
                if trust == "at"
                else "AT"
            )
            st_str = (
                f'<span color="{Colors.RED}"><b>ST</b></span>'
                if trust == "st"
                else "ST"
            )
            u_str = (
                f'<span color="{Colors.GREEN}"><u><b>U</b></u></span>'
                if trust == "u"
                else "U"
            )
        else:
            at_str = (
                f'<span color="{Colors.GREEN}"><u><b>AT</b></u></span>'
                if trust == "at"
                else "AT"
            )
            st_str = (
                f'<span color="{Colors.GREEN}"><u><b>ST</b></u></span>'
                if trust == "st"
                else "ST"
            )
            u_str = "U"

        return " / ".join([st_str, at_str, u_str])

    def __markup(self, value, options):

        idx = options.index(value) if value in options else -1
        return " / ".join(
            [f"<u><b>{o}</b></u>" if i == idx else o for i, o in enumerate(options)]
        )

    def __colors(self, access):
        a = access.upper()
        return (
            (Colors.LIGHT_GREEN, Colors.BLACK)
            if a == "A"
            else (Colors.ORANGE, Colors.BLACK)
            if a == "P"
            else (Colors.LIGHT_RED, Colors.WHITE)
        )

    def __handle_selection_changed(self, data):
        fileObjs = [datum[3] for datum in data] if data else None
        self.file_selection_changed(fileObjs)

    def __find_db_trust(self, subject):
        trust = subject.trust.lower()
        file = subject.file
        trustList = (
            self._systemTrust
            if trust == "st"
            else self._ancillaryTrust
            if trust == "at"
            else []
        )
        return first_true(trustList, pred=lambda x: x.path == file)

    def __show_reconciliation_dialog(self, subject):
        changeset = None
        parent = self.get_ref().get_toplevel()
        reconciliationDialog = TrustReconciliationDialog(
            subject, databaseTrust=self.__find_db_trust(subject), parent=parent
        ).get_ref()
        resp = reconciliationDialog.run()
        reconciliationDialog.destroy()
        if resp == _UNTRUST_RESP:
            changeset = Changeset()
            changeset.del_trust(subject.file)
        elif resp == _TRUST_RESP:
            changeset = Changeset()
            changeset.add_trust(subject.file)

        if changeset:
            dispatch(apply_changesets(changeset))

    def __apply_changeset_with_dialog(self, total_selections, changeset):
        action_items = changeset.get_path_action_map().items()
        additions = len([k for k, v in action_items if v.lower() == "add"])
        deletions = len([k for k, v in action_items if v.lower() == "del"])
        parent = self.get_ref().get_toplevel()
        confirmationDialog = ConfirmChangeDialog(
            parent=parent,
            total=total_selections,
            additions=additions,
            deletions=deletions,
        ).get_ref()
        confirm = confirmationDialog.run()
        confirmationDialog.destroy()
        if confirm == Gtk.ResponseType.YES:
            dispatch(apply_changesets(changeset))

    def _update_tree_count(self, count):
        label = FILE_LABEL if count == 1 else FILES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

    def load_store(self, subjects, **kwargs):
        self._systemTrust = kwargs.get("systemTrust", [])
        self._ancillaryTrust = kwargs.get("ancillaryTrust", [])
        store = Gtk.ListStore(str, str, str, object, str, str)
        for s in subjects:
            status = self._trust_markup(s)
            access = self.__markup(s.access.upper(), ["A", "P", "D"])
            bg_color, txt_color = self.__colors(s.access)
            store.append([status, access, s.file, s, bg_color, txt_color])
        super().load_store(store)

    def get_selected_row_by_file(self, file: str) -> Gtk.TreePath:
        return self.find_selected_row_by_data(file, 2)

    def on_view_row_activated(self, treeView, row, *args):
        model = treeView.get_model()
        iter_ = model.get_iter(row)
        subject = model.get_value(iter_, 3)
        self.__show_reconciliation_dialog(subject)

    def on_view_button_press_event(self, widget, event):
        if event.type != Gdk.EventType.BUTTON_PRESS or event.button != 3:
            return False

        treeView = self.get_object("treeView")
        model, pathlist = treeView.get_selection().get_selected_rows()
        path_at_pos = treeView.get_path_at_pos(int(event.x), int(event.y))
        path = next(iter(path_at_pos), None) if path_at_pos else None

        if path and path not in pathlist:
            treeView.get_selection().unselect_all()
            treeView.get_selection().select_path(path)
            model, pathlist = treeView.get_selection().get_selected_rows()
        n_paths = len(pathlist)

        if n_paths == 1:
            self.reconcileContextMenu.popup_at_pointer()
        elif n_paths > 1:
            trustable, untrustable = 0, 0
            subjects = [model.get_value(model.get_iter(p), 3) for p in pathlist]
            changeset = Changeset()
            for subject in subjects:
                db_trust = self.__find_db_trust(subject)
                status = db_trust.status.lower() if db_trust else None
                if not status or status == "d":
                    changeset.add_trust(subject.file)
                    trustable += 1
                elif status == "t" and subject.trust.lower() == "at":
                    changeset.del_trust(subject.file)
                    untrustable += 1

            self.fileChangeContextMenu.remove(self.fileChangeContextMenu.trustItem)
            self.fileChangeContextMenu.remove(
                self.fileChangeContextMenu.untrustItem
            )
            self.fileChangeContextMenu.trustItem.selection_data = None
            self.fileChangeContextMenu.untrustItem.selection_data = None

            if untrustable and not trustable:
                self.fileChangeContextMenu.append(
                    self.fileChangeContextMenu.untrustItem
                )
                self.fileChangeContextMenu.untrustItem.selection_data = (
                    len(subjects),
                    changeset,
                )
            elif trustable and not untrustable:
                self.fileChangeContextMenu.append(
                    self.fileChangeContextMenu.trustItem
                )
                self.fileChangeContextMenu.trustItem.selection_data = (
                    len(subjects),
                    changeset,
                )
            else:
                return True

            self.fileChangeContextMenu.show_all()
            self.fileChangeContextMenu.popup_at_pointer()

        return True

    def on_reconcile_file_activate(self, *args):
        treeView = self.get_object("treeView")
        model, pathlist = treeView.get_selection().get_selected_rows()
        iter_ = model.get_iter(next(iter(pathlist)))  # single select use first path
        subject = model.get_value(iter_, 3)
        self.__show_reconciliation_dialog(subject)

    def on_change_file_trust_activate(self, menu_item):
        self.__apply_changeset_with_dialog(*menu_item.selection_data)
