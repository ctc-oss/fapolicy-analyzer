import gi
from fapolicy_analyzer.app import System

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from enum import Enum

trustDb = "/home/addorschs/fapolicy-analyzer/py/tests/data/one.trust"
systemDb = "/var/lib/rpm"


class Trust_Database_Type(Enum):
    SYSTEM = 1
    ANCILLARY = 2


class TrustDatabaseAdmin:
    def __init__(self, trustDatabaseType):
        self.trustDatabaseType = trustDatabaseType
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../glade/trust_database_admin.glade")
        self.builder.connect_signals(self)

        self.databaseFileChooser = self.builder.get_object("databaseFileChooser")
        if self.trustDatabaseType == Trust_Database_Type.SYSTEM:
            self.databaseFileChooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
            self.databaseFileChooser.set_filename(systemDb)
        else:
            self.databaseFileChooser.set_action(Gtk.FileChooserAction.OPEN)
            self.databaseFileChooser.set_filename(trustDb)

    def __get_trust(self, file):
        if self.trustDatabaseType == Trust_Database_Type.SYSTEM:
            s = System(None, file, None)
            return s.system_trust()
        elif self.trustDatabaseType == Trust_Database_Type.ANCILLARY:
            s = System(None, None, file)
            return s.ancillary_trust()
        else:
            return []

    def get_content(self):
        return self.builder.get_object("trustDatabaseAdmin")

    def on_realize(self, *args):
        trust = self.__get_trust(self.databaseFileChooser.get_filename())
        trustStore = Gtk.ListStore(str, str, object)
        for i, e in enumerate(trust):
            trustStore.append([e.status, e.path, e])

        trustView = self.builder.get_object("trustView")
        trustView.set_model(trustStore)
        trustView.get_selection().connect(
            "changed", self.on_trust_view_selection_changed
        )
        for i, column in enumerate(["trust", "path"]):
            cell = Gtk.CellRendererText()
            trustView.append_column(Gtk.TreeViewColumn(column, cell, text=i))

    def on_trust_view_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            inDatabaseView = self.builder.get_object("inDatabaseView")
            e = model[treeiter][2]
            inDatabaseView.get_buffer().set_text(
                f"""File: {e.path}
Size: {e.size}
SHA256: {e.hash}
"""
            )

