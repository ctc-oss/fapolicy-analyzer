import gi
import re
import ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from os import path
from .searchable_list import SearchableList


class TrustFileList(SearchableList):
    def __init__(self, trust_func, markup_func=None, read_only=False):
        self.__events__ = [
            *super().__events__,
            "files_added",
            "files_deleted",
            "trust_selection_changed",
        ]
        buttons = [] if read_only else [self.__addButton()]

        super().__init__(self.__columns(), *buttons, searchColumnIndex=1)
        self.trust_func = trust_func
        self.markup_func = markup_func
        self.__load_data()
        self.selection_changed += self.__handle_selection_changed

    def __addButton(self):
        addBtn = Gtk.Button(
            label="Add",
            image=Gtk.Image.new_from_icon_name("list-add", 0),
            always_show_image=True,
        )
        addBtn.connect("clicked", self.on_addBtn_clicked)
        return addBtn

    def __columns(self):
        trustCell = Gtk.CellRendererText()
        trustCell.set_property("background", "light gray")
        trustColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_TRUST_HEADER, trustCell, markup=0
        )
        trustColumn.set_sort_column_id(0)
        fileColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_FILE_HEADER,
            Gtk.CellRendererText(),
            text=1,
            cell_background=3,
        )
        fileColumn.set_sort_column_id(1)
        return [trustColumn, fileColumn]

    def __handle_selection_changed(self, data):
        trust = data[2] if data else None
        self.trust_selection_changed(trust)

    def __load_data(self):
        super().set_loading(True)
        self.trust_func(self.load_store)

    def refresh(self):
        self.__load_data()

    def load_store(self, trust):
        store = Gtk.ListStore(str, str, object, str)
        for i, t in enumerate(trust):
            status, *rest = (
                self.markup_func(t.status) if self.markup_func else (t.status,)
            )
            bgColor = rest[0] if rest else "white"
            store.append([status, t.path, t, bgColor])

        super().load_store(store)

    def on_addBtn_clicked(self, *args):
        fcd = Gtk.FileChooserDialog(
            title=strings.ADD_FILE_BUTTON_LABEL,
            transient_for=self.get_ref().get_toplevel(),
            action=Gtk.FileChooserAction.OPEN,
        )
        fcd.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_ADD,
            Gtk.ResponseType.OK,
        )
        fcd.set_select_multiple(True)
        response = fcd.run()
        fcd.hide()
        if response == Gtk.ResponseType.OK:
            files = [f for f in fcd.get_filenames() if path.isfile(f)]

            # -- Filter to address fapolicyd embeded whitspace in path issue
            #     Current fapolicyd VT.B.D. When fixed remove this block
            #
            # Detect and remove file paths w/embedded spaces. Alert user w/dlg
            print("Filtering out paths with embedded whitespace")
            listAccepted = [e for e in files if not re.search(r"\s", e)]
            listRejected = [e for e in files if re.search(r"\s", e)]
            if listRejected:
                dlgWhitespaceInfo = Gtk.MessageDialog(
                    transient_for=self.get_ref().get_toplevel(),
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=strings.WHITESPACE_WARNING_DIALOG_TITLE,
                )

                # Convert list of paths to a single string
                strListRejected = "\n".join(listRejected)

                dlgWhitespaceInfo.format_secondary_text(
                    strings.WHITESPACE_WARNING_DIALOG_TEXT + strListRejected
                )
                dlgWhitespaceInfo.run()
                dlgWhitespaceInfo.destroy()
            files = listAccepted
            #     Remove this filter block if fapolicyd bug #TBD is fixed
            # ----------------------------------------------------------------

            if files:
                self.files_added(files)
        fcd.destroy()
