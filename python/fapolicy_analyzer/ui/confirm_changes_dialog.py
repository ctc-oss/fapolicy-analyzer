#!/usr/bin/python
# confirm_changes_dialog.py - A dialog with an embedded scrollable filelist
# TPArchambault 2021.05.24
#

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ConfirmInfoDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="Confirm Changes to Deploy", transient_for=parent, flags=0)
        self.add_buttons( Gtk.STOCK_CANCEL,
                          Gtk.ResponseType.CANCEL,
                          Gtk.STOCK_OK,
                          Gtk.ResponseType.OK)

        self.set_default_size(500, 200)

        label = Gtk.Label(label="The following changes will be deployed: ")

        self.scrolled_window = Gtk.ScrolledWindow()
        self.changeStore = Gtk.ListStore(str, str)
        self.tree_view = Gtk.TreeView(model=self.changeStore)
        
        actionCell  = Gtk.CellRendererText()
        actionCell.set_property("background", "light gray")
        actionColumn = Gtk.TreeViewColumn("Action", actionCell, markup=0)
        self.tree_view.append_column(actionColumn)
        actionColumn.set_sort_column_id(0)
        fileColumn = Gtk.TreeViewColumn("File", Gtk.CellRendererText(),
                                        text=1, cell_background=3)
        self.tree_view.append_column(fileColumn)
        fileColumn.set_sort_column_id(1)
        self.scrolled_window.add(self.tree_view)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC,
                                        Gtk.PolicyType.ALWAYS)
        
        box = self.get_content_area()
        box.add(label)
        box.pack_start(self.scrolled_window, True, True, 0)
        
        self.show_all()

    def load_path_action_list(self, listPathActionPairs):
        if listPathActionPairs:
            for e in listPathActionPairs:
                self.changeStore.append(e)
        
class DialogWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Dialog Example")
        self.set_border_width(6)
        button = Gtk.Button(label="Open dialog")
        button.connect("clicked", self.on_button_clicked)
        self.add(button)

    def on_button_clicked(self, widget):
        dialog = ConfirmInfoDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()
        
def main():
    win = DialogWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
    
