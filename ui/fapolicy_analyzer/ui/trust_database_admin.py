import gi
from fapolicy_analyzer.app import System

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from enum import Enum

trustFile = "/home/addorschs/fapolicy-analyzer/tests/data/fapolicyd.trust"


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
            self.databaseFileChooser.set_filename("/var/lib/rpm")
        else:
            self.databaseFileChooser.set_action(Gtk.FileChooserAction.OPEN)
            self.databaseFileChooser.set_filename(trustFile)

    def __get_trust(self, file):
        if self.trustDatabaseType == Trust_Database_Type.SYSTEM:
            s = System(trustFile, file)
            return s.system_trust()
        elif self.trustDatabaseType == Trust_Database_Type.ANCILLARY:
            s = System(file, None)
            return s.ancillary_trust()
        else:
            return []

    def get_content(self):
        return self.builder.get_object("trustDatabaseAdmin")

    def on_realize(self, *args):
        trust = self.__get_trust(self.databaseFileChooser.get_filename())
        trustStore = Gtk.ListStore(str, str, object)
        for i, e in enumerate(trust):
            trustStore.append(["T/U", e.path, e])
            # the treeview breaks with too many entries, need to figure out some paging mechanism
            # if i == 100:
            #     break

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

