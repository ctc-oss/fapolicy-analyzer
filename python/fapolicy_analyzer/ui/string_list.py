import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .searchable_list import SearchableList


class StringList(SearchableList):
    def __init__(self, label=None, label_plural=None):
        super().__init__(self.__columns(), view_headers_visible=False)

        self.label = label
        self.label_plural = (
            f"{label}s" if label_plural is None and label is not None else label_plural
        )

    def __columns(self):
        return [Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=0)]

    def _update_tree_count(self, count):
        lbl = self.label if count == 1 else self.label_plural
        self.treeCount.set_text(" ".join([str(count), lbl or ""]).strip())

    def load_store(self, strs):
        store = Gtk.ListStore(str)

        for s in strs:
            store.append([s])

        super().load_store(store)
