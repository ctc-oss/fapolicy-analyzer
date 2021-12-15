import fapolicy_analyzer.ui.strings as strings
import gi

gi.require_version("Gtk", "3.0")
from fapolicy_analyzer import Changeset
from gi.repository import Gdk, Gtk
from more_itertools import first_true

from .actions import apply_changesets
from .add_file_button import AddFileButton
from .configs import Colors
from .searchable_list import SearchableList
from .store import dispatch
from .strings import FILE_LABEL, FILES_LABEL
from .trust_reconciliation_dialog import TrustReconciliationDialog

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
        )

        self._systemTrust = []
        self._ancillaryTrust = []
        self.contextMenu = self.__build_context_menu()
        self.load_store([])
        self.selection_changed += self.__handle_selection_changed
        self.get_object("treeView").connect("row-activated", self.on_view_row_activated)
        self.get_object("treeView").connect(
            "button-press-event", self.on_view_button_press_event
        )

    def __build_context_menu(self):
        menu = Gtk.Menu()
        reconcileItem = Gtk.MenuItem.new_with_label("Reconcile File")
        reconcileItem.connect("activate", self.on_reconcile_file_activate)
        menu.append(reconcileItem)
        menu.show_all()
        return menu

    def _columns(self):
        trustCell = Gtk.CellRendererText()
        trustCell.set_property("background", "light gray")
        trustColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_TRUST_HEADER, trustCell, markup=0
        )
        trustColumn.set_sort_column_id(0)
        accessCell = Gtk.CellRendererText()
        accessCell.set_property("background", "light gray")
        accessColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_ACCESS_HEADER, accessCell, markup=1
        )
        accessColumn.set_sort_column_id(1)
        fileColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_FILE_HEADER,
            Gtk.CellRendererText(),
            text=2,
            cell_background=4,
        )
        fileColumn.set_sort_column_id(2)
        return [trustColumn, accessColumn, fileColumn]

    def __markup(self, value, options):
        idx = options.index(value) if value in options else -1
        return "/".join(
            [f"<b><u>{o}</u></b>" if i == idx else o for i, o in enumerate(options)]
        )

    def __color(self, access):
        a = access.upper()
        return (
            Colors.LIGHT_GREEN
            if a == "A"
            else Colors.ORANGE
            if a == "P"
            else Colors.LIGHT_RED
        )

    def __handle_selection_changed(self, data):
        fileObjs = [datum[3] for datum in data] if data else None
#        for fileObj in fileObjs: 
        fileObj = fileObjs[-1]
        self.file_selection_changed(fileObj)
                


    def __show_reconciliation_dialog(self, subject):
        def find_db_trust(subject):
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

        changeset = None
        parent = self.get_ref().get_toplevel()
        reconciliationDialog = TrustReconciliationDialog(
            subject, databaseTrust=find_db_trust(subject), parent=parent
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

    def _update_tree_count(self, count):
        label = FILE_LABEL if count == 1 else FILES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

    def load_store(self, subjects, **kwargs):
        self._systemTrust = kwargs.get("systemTrust", [])
        self._ancillaryTrust = kwargs.get("ancillaryTrust", [])
        store = Gtk.ListStore(str, str, str, object, str)
        for s in subjects:
            status = self.__markup(s.trust.upper(), ["ST", "AT", "U"])
            access = self.__markup(s.access.upper(), ["A", "P", "D"])
            bgColor = self.__color(s.access)
            store.append([status, access, s.file, s, bgColor])

        super().load_store(store)

    def on_view_row_activated(self, treeView, row, *args):
        model = treeView.get_model()
        iter_ = model.get_iter(row)
        subject = model.get_value(iter_, 3)
        self.__show_reconciliation_dialog(subject)

    def on_view_button_press_event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.contextMenu.popup_at_pointer()

    def on_reconcile_file_activate(self, *args):
        treeView = self.get_object("treeView")
        model, pathlist = treeView.get_selection().get_selected_rows()
        iter_ = model.get_iter(next(iter(pathlist)))  # single select use first path
        subject = model.get_value(iter_, 3)
        self.__show_reconciliation_dialog(subject)
