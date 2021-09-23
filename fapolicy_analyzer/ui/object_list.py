import gi
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from concurrent.futures import ThreadPoolExecutor
from .add_file_button import AddFileButton
from .configs import Colors
from .searchable_list import SearchableList
from .strings import FILE_LABEL, FILES_LABEL


class ObjectList(SearchableList):
    def __init__(self):
        self.__events__ = [
            *super().__events__,
            "object_selection_changed",
        ]

        add_button = AddFileButton()
        add_button.files_added += lambda files: print(files)
        add_button.get_ref().set_sensitive(False)  # disable for now in readonly-view

        super().__init__(
            self.__columns(),
            add_button.get_ref(),
            searchColumnIndex=3,
            defaultSortIndex=3,
        )

        self.executor = ThreadPoolExecutor(max_workers=1)
        self.load_store([])
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
            else Colors.LIGHT_GREEN
            if numModes > 0
            else Colors.LIGHT_RED
        )

    def __handle_selection_changed(self, data):
        object = data[4] if data else None
        self.object_selection_changed(object)

    def _update_tree_count(self, count):
        label = FILE_LABEL if count == 1 else FILES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

    def load_store(self, objects):
        store = Gtk.ListStore(str, str, str, str, object, str)
        for o in objects:
            status = self.__markup(o.trust.upper(), ["ST", "AT", "U"])
            mode = self.__markup(
                o.mode.upper(),
                ["R", "W", "X"],
                seperator="",
                multiValue=True,
            )
            access = self.__markup(o.access.upper(), ["A", "D"])
            bgColor = self.__color(o.access, o.mode)
            store.append([status, mode, access, o.file, o, bgColor])

        super().load_store(store)
