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


def _mock_objects():
    statuses = ["ST", "AT", "U"]
    modes = ["R", "W", "X", "RW", "RX", "WX", "RWX", ""]
    accesses = ["A", "D"]
    locations = ["/usr/sbin", "/usr/bin", "/usr/local/sbin", "/usr/local/bin"]
    paths = subprocess.getstatusoutput(
        f"find {' '.join(locations)} -executable -type f"
    )
    return [
        {
            "status": statuses[randrange(3)],
            "mode": modes[randrange(8)],
            "access": accesses[randrange(2)],
            "path": p,
        }
        for p in paths[1].splitlines()
    ]


class ObjectList(SearchableList):
    def __init__(self):
        self.__events__ = [
            *super().__events__,
            "object_selection_changed",
        ]

        add_button = AddFileButton()
        add_button.files_added += lambda files: print(files)

        super().__init__(self.__columns(), add_button.get_ref(), searchColumnIndex=3)

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
        modeCell = Gtk.CellRendererText()
        modeCell.set_property("background", "light gray")
        modeColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_MODE_HEADER, modeCell, markup=1
        )
        modeColumn.set_sort_column_id(1)
        accessCell = Gtk.CellRendererText()
        accessCell.set_property("background", "light gray")
        accessColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_ACCESS_HEADER, accessCell, markup=2
        )
        accessColumn.set_sort_column_id(2)
        fileColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_FILE_HEADER,
            Gtk.CellRendererText(),
            text=3,
            cell_background=5,
        )
        fileColumn.set_sort_column_id(3)
        return [trustColumn, modeColumn, accessColumn, fileColumn]

    def __markup(self, value, options, seperator="/", multiValue=False):
        def wrap(x):
            return f"<b><u>{x}</u></b>"

        valueSet = set(value.upper()) if multiValue else {value.upper()}
        matches = set(options).intersection(valueSet)
        return seperator.join([wrap(o) if o in matches else o for o in options])

    def __color(self, access, mode):
        if access.upper() != "A":
            return Colors.LIGHT_RED

        numModes = len(set(mode.upper()).intersection({"R", "W", "X"}))
        return (
            Colors.LIGHT_GREEN
            if numModes == 3
            else Colors.LIGHT_YELLOW
            if numModes > 0
            else Colors.LIGHT_RED
        )

    def _load_data(self):
        def get_objects():
            objects = _mock_objects()
            GLib.idle_add(self.load_store, objects)

        super().set_loading(True)
        self.executor.submit(get_objects)

    def __handle_selection_changed(self, data):
        object = data[4] if data else None
        self.object_selection_changed(object)

    def _update_tree_count(self, count):
        label = FILE_LABEL if count == 1 else FILES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

    def load_store(self, objects):
        store = Gtk.ListStore(str, str, str, str, object, str)
        for i, o in enumerate(objects):
            status = self.__markup(o.get("status", "").upper(), ["ST", "AT", "U"])
            mode = self.__markup(
                o.get("mode", "").upper(),
                ["R", "W", "X"],
                seperator="",
                multiValue=True,
            )
            access = self.__markup(o.get("access", "").upper(), ["A", "D"])
            bgColor = self.__color(o.get("access", ""), o.get("mode", ""))
            store.append([status, mode, access, o.get("path", ""), o, bgColor])

        super().load_store(store)
