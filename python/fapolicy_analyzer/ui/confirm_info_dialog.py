import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import ui.strings as strings


class ConfirmInfoDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, strings.DEPLOY_ANCILLARY_CONFIRM_DIALOG_TITLE,
                            transient_for=parent, flags=0)

        self.add_buttons(Gtk.STOCK_NO,
                         Gtk.ResponseType.NO,
                         Gtk.STOCK_YES,
                         Gtk.ResponseType.YES)

        self.set_default_size(-1, 200)

        label = Gtk.Label(label=strings.DEPLOY_ANCILLARY_CONFIRM_DIALOG_TEXT)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.changeStore = Gtk.ListStore(str, str)
        self.tree_view = Gtk.TreeView(model=self.changeStore)

        cellAction = Gtk.CellRendererText()
        cellAction.set_property("background", "light gray")
        columnAction = Gtk.TreeViewColumn(strings.DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR,
                                          cellAction, markup=0)
        self.tree_view.append_column(columnAction)
        columnAction.set_sort_column_id(0)

        cellFile = Gtk.CellRendererText()
        columnFile = Gtk.TreeViewColumn(strings.DEPLOY_ANCILLARY_CONFIRM_DLG_PATH_COL_HDR,
                                        cellFile, text=1)

        self.tree_view.append_column(columnFile)
        columnFile.set_sort_column_id(1)
        self.scrolled_window.add(self.tree_view)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER,
                                        Gtk.PolicyType.ALWAYS)

        box = self.get_content_area()
        box.add(label)
        box.pack_start(self.scrolled_window, True, True, 0)

        self.show_all()

    def load_path_action_list(self, listPathActionPairs):
        if listPathActionPairs:
            for e in listPathActionPairs:
                # tuples are in (path,action) order, displayed as (action,path)
                self.changeStore.append(e[::-1])
