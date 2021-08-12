import gi

gi.require_version("Gtk", "3.0")
from events import Events
from gi.repository import Gtk
from .loader import Loader
from .ui_widget import UIWidget


class SearchableList(UIWidget, Events):
    __events__ = ["selection_changed"]

    def __init__(
        self,
        columns,
        *actionButtons,
        searchColumnIndex=0,
        view_headers_visible=True,
    ):
        UIWidget.__init__(self, "searchable_list")
        Events.__init__(self)

        self.searchColumnIndex = searchColumnIndex
        self.treeCount = self.get_object("treeCount")
        self.treeView = self.get_object("treeView")
        self.treeView.set_headers_visible(view_headers_visible)
        for column in columns:
            self.treeView.append_column(column)

        self.search = self.get_object("search")
        self.viewSwitcher = self.get_object("viewStack")
        self.viewSwitcher.add_named(Loader().get_ref(), "loader")

        buttonGroup = self.get_object("actionButtons")
        if actionButtons:
            for button in actionButtons:
                buttonGroup.pack_start(button, False, True, 0)
                buttonGroup.show_all()
        else:
            buttonGroup.get_parent().remove(buttonGroup)

    def __filter_view(self, model, iter, data):
        filter = self.get_object("search").get_text()
        return True if not filter else filter in model[iter][self.searchColumnIndex]

    def __get_tree_count(self):
        return self.treeViewFilter.iter_n_children(None)

    def _load_data(self):
        pass

    def _update_tree_count(self, count):
        self.treeCount.set_text(str(count))

    def load_store(self, store):
        self.treeViewFilter = store.filter_new()
        self.treeViewFilter.set_visible_func(self.__filter_view)
        self.treeView.set_model(Gtk.TreeModelSort(model=self.treeViewFilter))
        self.treeView.get_selection().connect("changed", self.on_view_selection_changed)
        self._update_tree_count(self.__get_tree_count())
        self.set_loading(False)

    def set_loading(self, loading):
        if loading:
            self.viewSwitcher.set_visible_child_name("loader")
            self.search.set_sensitive(False)
        else:
            self.viewSwitcher.set_visible_child_name("treeView")
            self.search.set_sensitive(True)

    def refresh(self):
        self._load_data()

    def on_view_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        data = model[treeiter] if model and treeiter else []
        self.selection_changed(data)

    def on_search_changed(self, search):
        self.treeViewFilter.refilter()
        self._update_tree_count(self.__get_tree_count())
