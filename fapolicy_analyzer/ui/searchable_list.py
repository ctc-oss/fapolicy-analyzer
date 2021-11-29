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
        defaultSortIndex=0,
        defaultSortDirection=Gtk.SortType.DESCENDING,
        view_headers_visible=True,
    ):
        UIWidget.__init__(self, "searchable_list")
        Events.__init__(self)

        self.searchColumnIndex = searchColumnIndex
        self.defaultSortIndex = defaultSortIndex
        self.defaultSortDirection = defaultSortDirection
        self.treeCount = self.get_object("treeCount")
        self.treeView = self.get_object("treeView")
        self.treeView.set_headers_visible(view_headers_visible)
        for column in columns:
            self.treeView.append_column(column)

        self.search = self.get_object("search")
        self.viewSwitcher = self.get_object("viewStack")
        self.viewSwitcher.add_named(Loader().get_ref(), "loader")
        self.set_action_buttons(*actionButtons)

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
        def apply_prev_sort(model):
            if currentModel := self.treeView.get_model():
                currentSort = currentModel.get_sort_column_id()
            else:
                currentSort = (self.defaultSortIndex, 0)

            model.set_sort_column_id(*currentSort)
            return model

        self.treeViewFilter = store.filter_new()
        self.treeViewFilter.set_visible_func(self.__filter_view)

        sortableModel = apply_prev_sort(Gtk.TreeModelSort(model=self.treeViewFilter))
        self.treeView.set_model(sortableModel)

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

    def set_action_buttons(self, *buttons):
        buttonGroup = self.get_object("actionButtons")

        # remove all buttons
        buttonGroup.foreach(lambda btn: buttonGroup.remove(btn))

        if not buttons:
            buttonGroup.hide()
            return

        for button in buttons:
            buttonGroup.pack_start(button, False, True, 0)
            buttonGroup.show_all()

    def get_action_buttons(self):
        return self.get_object("actionButtons").get_children()

    def on_view_selection_changed(self, selection):
        model, treeiter = selection.get_selected_rows()
        if model and treeiter:
            if len(treeiter) == 1:
                data = model[treeiter]
                self.selection_changed(data)        
            else:
                data = [model[i] for i in treeiter]
                for datum in data:
                    self.selection_changed(datum)
        else:
            data = []

    def on_search_changed(self, search):
        self.treeViewFilter.refilter()
        self._update_tree_count(self.__get_tree_count())
