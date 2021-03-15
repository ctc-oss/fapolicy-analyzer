import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from events import Events


class TrustFileList(Events):
    __events__ = ("on_file_selection_change", "on_database_selection_change")

    def __init__(self, locationAction=Gtk.FileChooserAction.OPEN, defaultLocation=None):
        super(TrustFileList, self).__init__()
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
        self.viewSwitcher = self.builder.get_object("trustViewStack")

    def set_loading(self, loading):
        if loading:
            self.viewSwitcher.set_visible_child_name("trustViewLoader")
        else:
            self.viewSwitcher.set_visible_child_name("trustView")

    def get_content(self):
        return self.builder.get_object("trustFileList")

    def get_selected_location(self):
        return self.databaseFileChooser.get_filename()

    def on_databaseFileChooser_selection_changed(self, *args):
        self.on_database_selection_change(self.databaseFileChooser.get_filename())

    def set_trust(self, trust, markup_func=None):
        trustStore = Gtk.ListStore(str, str, object, str)
        for i, e in enumerate(trust):
            status, *rest = markup_func(e.status) if markup_func else (e.status,)
            bgColor = rest[0] if rest else "white"
            trustStore.append([status, e.path, e, bgColor])
        self.trustView.set_model(trustStore)
        self.trustView.get_selection().connect(
            "changed", self.__on_trust_view_selection_changed
        )
        self.set_loading(False)

    def __on_trust_view_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        trust = model[treeiter][2] if treeiter is not None else {}
        self.on_file_selection_change(trust)
