import gi
import subprocess
import ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from concurrent.futures import ThreadPoolExecutor
from random import randrange
from .add_file_button import AddFileButton
from .configs import Colors
from .searchable_list import SearchableList
from .strings import FILE_LABEL, FILES_LABEL


def _mock_subjects():
    statuses = ["ST", "AT", "U"]
    accesses = ["A", "P", "D"]
    locations = ["/usr/sbin", "/usr/bin", "/usr/local/sbin", "/usr/local/bin"]
    paths = subprocess.getstatusoutput(
        f"find {' '.join(locations)} -executable -type f"
    )
    return [
        {"status": statuses[randrange(3)], "access": accesses[randrange(3)], "path": p}
        for p in paths[1].splitlines()
    ]


class SubjectList(SearchableList):
    def __init__(self):
        self.__events__ = [
            *super().__events__,
            "subject_selection_changed",
        ]

        add_button = AddFileButton()
        add_button.files_added += lambda files: print(files)

        super().__init__(self.__columns(), add_button.get_ref(), searchColumnIndex=2)

        self.executor = ThreadPoolExecutor(max_workers=1)
        self._load_data()
        self.selection_changed += self.__handle_selection_changed

    def __columns(self):
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
            else Colors.LIGHT_YELLOW
            if a == "P"
            else Colors.LIGHT_RED
        )

    def _load_data(self):
        def get_subjects():
            subjects = _mock_subjects()
            GLib.idle_add(self.load_store, subjects)

        super().set_loading(True)
        self.executor.submit(get_subjects)

    def __handle_selection_changed(self, data):
        subject = data[3] if data else None
        self.subject_selection_changed(subject)

    def _update_tree_count(self, count):
        label = FILE_LABEL if count == 1 else FILES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

    def load_store(self, subjects):
        store = Gtk.ListStore(str, str, str, object, str)
        for i, s in enumerate(subjects):
            status = self.__markup(s.get("status", "").upper(), ["ST", "AT", "U"])
            access = self.__markup(s.get("access", "").upper(), ["A", "P", "D"])
            bgColor = self.__color(s.get("access", ""))
            store.append([status, access, s.get("path", ""), s, bgColor])

        super().load_store(store)
