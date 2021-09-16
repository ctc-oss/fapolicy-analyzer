import gi
import fapolicy_analyzer.ui.strings as strings

from time import localtime, strftime

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .searchable_list import SearchableList
from .strings import FILE_LABEL, FILES_LABEL


class TrustFileList(SearchableList):
    def __init__(self, trust_func, markup_func=None, *args):
        self.__events__ = [
            *super().__events__,
            "files_added",
            "files_deleted",
            "trust_selection_changed",
        ]

        super().__init__(
            self._columns(), *args, searchColumnIndex=1, defaultSortIndex=1
        )
        self.trust_func = trust_func
        self.markup_func = markup_func
        self.refresh()
        self.selection_changed += self.__handle_selection_changed

    def __handle_selection_changed(self, data):
        trust = data[3] if data else None
        self.trust_selection_changed(trust)

    def _columns(self):
        # trust status column
        trustColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_TRUST_HEADER,
            Gtk.CellRendererText(background="light gray"),
            markup=0,
        )
        trustColumn.set_sort_column_id(0)

        # modification time column
        mtimeColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_MTIME_HEADER,
            Gtk.CellRendererText(),
            text=1,
            cell_background=3,
        )
        mtimeColumn.set_sort_column_id(1)

        # fullpath column
        fileColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_FILE_HEADER,
            Gtk.CellRendererText(),
            text=2,
            cell_background=3,
        )
        fileColumn.set_sort_column_id(2)
        return [trustColumn, mtimeColumn, fileColumn]

    def _update_tree_count(self, count):
        label = FILE_LABEL if count == 1 else FILES_LABEL
        self.treeCount.set_text(" ".join([str(count), label]))

    def refresh(self):
        super().set_loading(True)
        self.trust_func(self.load_trust)

    def load_trust(self, trust):
        store = Gtk.ListStore(str, str, str, object, str)
        for i, data in enumerate(trust):
            status, *rest = (
                self.markup_func(data.status) if self.markup_func else (data.status,)
            )
            bgColor = rest[0] if rest else "white"
            strDateTime = (
                strftime("%Y.%m.%d %H:%M:%S", localtime(data.actual.last_modified))
                if data.actual
                else "Missing"
            )
            store.append([status, strDateTime, data.path, data, bgColor])

        self.load_store(store)
