import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from events import Events


class TrustFileList(Events):
    __events__ = "on_file_selection_change"

    def __init__(self, locationAction=Gtk.FileChooserAction.OPEN, defaultLocation=None):
        super(TrustFileList, self).__init__()
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/trust_file_list.glade")
        self.builder.connect_signals(self)

        self.databaseFileChooser = self.builder.get_object("databaseFileChooser")
        self.databaseFileChooser.set_action(locationAction)
        self.databaseFileChooser.set_filename(defaultLocation)

        self.trustView = self.builder.get_object("trustView")
        self.trustView.append_column(
            Gtk.TreeViewColumn("trust", Gtk.CellRendererText(), markup=0)
        )
        self.trustView.append_column(
            Gtk.TreeViewColumn("path", Gtk.CellRendererText(), text=1)
        )

    def get_content(self):
        return self.builder.get_object("trustFileList")

    def get_selected_location(self):
        return self.databaseFileChooser.get_filename()

    def set_list_store(self, store):
        self.trustView.set_model(store)
        self.trustView.get_selection().connect(
            "changed", self.__on_trust_view_selection_changed
        )

    def __on_trust_view_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        trust = model[treeiter][2] if treeiter is not None else {}
        self.on_file_selection_change(trust)
