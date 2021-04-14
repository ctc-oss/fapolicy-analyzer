import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf
from threading import Thread
from time import sleep
from events import Events
from .ui_widget import UIWidget


class TrustFileList(UIWidget, Events):
    __events__ = "on_file_selection_change"

    def __init__(self, trust_func, markup_func=None):
        UIWidget.__init__(self)
        Events.__init__(self)
        self.trust_func = trust_func
        self.markup_func = markup_func

        self.trustView = self.builder.get_object("trustView")
        trustCell = Gtk.CellRendererText()
        trustCell.set_property("background", "light gray")
        trustColumn = Gtk.TreeViewColumn("Trust", trustCell, markup=0)
        trustColumn.set_sort_column_id(0)
        self.trustView.append_column(trustColumn)
        fileColumn = Gtk.TreeViewColumn(
            "File", Gtk.CellRendererText(), text=1, cell_background=3
        )
        fileColumn.set_sort_column_id(1)
        self.trustView.append_column(fileColumn)

        loader = self.builder.get_object("trustViewLoader")
        loader.set_from_animation(
            GdkPixbuf.PixbufAnimation.new_from_file(
                self.absolute_file_path("../../resources/filled_fading_balls.gif")
            )
        )

        self.__set_loading(True)
        thread = Thread(target=self.__get_trust)
        thread.daemon = True
        thread.start()

    def __get_trust(self):
        sleep(0.1)
        trust = self.trust_func()

        trustStore = Gtk.ListStore(str, str, object, str)
        for i, e in enumerate(trust):
            status, *rest = (
                self.markup_func(e.status) if self.markup_func else (e.status,)
            )
            bgColor = rest[0] if rest else "white"
            trustStore.append([status, e.path, e, bgColor])

        GLib.idle_add(self.__load_trust_store, trustStore)

    def __load_trust_store(self, trustStore):
        self.trustViewFilter = trustStore.filter_new()
        self.trustViewFilter.set_visible_func(self.__filter_trust_view)
        self.trustView.set_model(Gtk.TreeModelSort(model=self.trustViewFilter))
        self.trustView.get_selection().connect(
            "changed", self.on_trust_view_selection_changed
        )
        self.__set_loading(False)

    def __filter_trust_view(self, model, iter, data):
        filter = self.builder.get_object("trustViewSearch").get_text()
        return True if not filter else filter in model[iter][1]

    def __set_loading(self, loading):
        viewSwitcher = self.builder.get_object("trustViewStack")
        trustViewSearch = self.builder.get_object("trustViewSearch")
        if loading:
            viewSwitcher.set_visible_child_name("trustViewLoader")
            trustViewSearch.set_sensitive(False)
        else:
            viewSwitcher.set_visible_child_name("trustView")
            trustViewSearch.set_sensitive(True)

    def get_content(self):
        return self.builder.get_object("trustFileList")

    def on_trust_view_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        trust = model[treeiter][2] if treeiter is not None else {}
        self.on_file_selection_change(trust)

    def on_search_changed(self, search):
        self.trustViewFilter.refilter()

    def on_trustFileList_realize(self, *args):
        return
        # print("***** on realized")
        # if self.trust_func:
        #     self.__set_loading(True)
        #     thread = Thread(target=self.__get_trust)
        #     thread.daemon = True
        #     thread.start()
