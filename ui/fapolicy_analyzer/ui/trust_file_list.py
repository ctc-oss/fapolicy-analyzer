import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf
from threading import Thread
from time import sleep
from events import Events
from fapolicy_analyzer.app import System


class TrustFileList(Events):
    __events__ = "on_file_selection_change"

    def __init__(
        self,
        locationAction=Gtk.FileChooserAction.OPEN,
        defaultLocation=None,
        trust_func=lambda x: System(None, None, x).ancillary_trust(),
        markup_func=None,
    ):
        super(TrustFileList, self).__init__()
        self.trust_func = trust_func
        self.markup_func = markup_func
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/trust_file_list.glade")
        self.builder.connect_signals(self)

        self.databaseFileChooser = self.builder.get_object("databaseFileChooser")
        self.databaseFileChooser.set_action(locationAction)
        if defaultLocation:
            self.databaseFileChooser.set_filename(defaultLocation)

        self.trustView = self.builder.get_object("trustView")
        trustCell = Gtk.CellRendererText()
        trustCell.set_property("background", "light gray")
        self.trustView.append_column(Gtk.TreeViewColumn("Trust", trustCell, markup=0))
        self.trustView.append_column(
            Gtk.TreeViewColumn(
                "File", Gtk.CellRendererText(), text=1, cell_background=3
            )
        )

        loader = self.builder.get_object("trustViewLoader")
        loader.set_from_animation(
            GdkPixbuf.PixbufAnimation.new_from_file(
                "../resources/filled_fading_balls.gif"
            )
        )

    def __get_trust(self, database):
        sleep(0.1)
        trust = self.trust_func(database)

        trustStore = Gtk.ListStore(str, str, object, str)
        for i, e in enumerate(trust):
            status, *rest = (
                self.markup_func(e.status) if self.markup_func else (e.status,)
            )
            bgColor = rest[0] if rest else "white"
            trustStore.append([status, e.path, e, bgColor])

        GLib.idle_add(self.__load_trust_store, trustStore)

    def __load_trust_store(self, trustStore):
        self.trustView.set_model(trustStore)
        self.trustView.get_selection().connect(
            "changed", self.__on_trust_view_selection_changed
        )
        self.__set_loading(False)

    def __set_loading(self, loading):
        viewSwitcher = self.builder.get_object("trustViewStack")
        if loading:
            viewSwitcher.set_visible_child_name("trustViewLoader")
        else:
            viewSwitcher.set_visible_child_name("trustView")

    def __on_trust_view_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        trust = model[treeiter][2] if treeiter is not None else {}
        self.on_file_selection_change(trust)

    def get_content(self):
        return self.builder.get_object("trustFileList")

    def on_databaseFileChooser_selection_changed(self, *args):
        database = self.databaseFileChooser.get_filename()
        if database and self.trust_func:
            self.__set_loading(True)
            thread = Thread(target=self.__get_trust, args=(database,))
            thread.daemon = True
            thread.start()
