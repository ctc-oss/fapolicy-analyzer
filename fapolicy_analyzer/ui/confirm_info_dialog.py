import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .strings import (
    CHANGESET_ACTION_ADD,
    CHANGESET_ACTION_DEL,
    DEPLOY_ANCILLARY_CONFIRM_DIALOG_TEXT,
    DEPLOY_ANCILLARY_CONFIRM_DIALOG_TITLE,
    DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR,
    DEPLOY_ANCILLARY_CONFIRM_DLG_PATH_COL_HDR,
)


class ConfirmInfoDialog(Gtk.Dialog):
    def __init__(self, parent=None, listPathActionPairs=[]):
        Gtk.Dialog.__init__(
            self,
            title=DEPLOY_ANCILLARY_CONFIRM_DIALOG_TITLE,
            transient_for=parent,
            flags=0,
        )

        self.add_buttons(
            Gtk.STOCK_NO, Gtk.ResponseType.NO, Gtk.STOCK_YES, Gtk.ResponseType.YES
        )

        self.set_default_size(-1, 200)

        changeStore = Gtk.ListStore(str, str)
        self.__load_path_action_list(changeStore, listPathActionPairs)
        tree_view = Gtk.TreeView(model=changeStore)
        tree_view.get_selection().set_mode(Gtk.SelectionMode.NONE)

        columnAction = Gtk.TreeViewColumn(
            DEPLOY_ANCILLARY_CONFIRM_DLG_ACTION_COL_HDR,
            Gtk.CellRendererText(background="light gray"),
            text=0,
        )
        columnAction.set_sort_column_id(0)
        tree_view.append_column(columnAction)

        columnFile = Gtk.TreeViewColumn(
            DEPLOY_ANCILLARY_CONFIRM_DLG_PATH_COL_HDR, Gtk.CellRendererText(), text=1
        )
        columnFile.set_sort_column_id(1)
        tree_view.append_column(columnFile)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(tree_view)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)

        box = self.get_content_area()
        box.add(Gtk.Label(label=DEPLOY_ANCILLARY_CONFIRM_DIALOG_TEXT))
        box.pack_start(scrolled_window, True, True, 0)

        self.show_all()

    def __load_path_action_list(self, store, listPathActionPairs):
        if listPathActionPairs:
            for e in listPathActionPairs:
                # tuples are in (path,action) order, displayed as (action,path)
                action = (
                    CHANGESET_ACTION_ADD
                    if e[-1] == "Add"
                    else CHANGESET_ACTION_DEL
                    if e[-1] == "Del"
                    else ""
                )
                store.append((action, e[0]))
