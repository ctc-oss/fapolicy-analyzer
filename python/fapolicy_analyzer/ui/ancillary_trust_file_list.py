import gi
import re
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from functools import reduce
from gi.repository import Gtk
from os import path
from types import SimpleNamespace
from .configs import Colors
from .state_manager import stateManager
from .trust_file_list import TrustFileList


class AncillaryTrustFileList(TrustFileList):
    def __init__(self, trust_func):
        addBtn = Gtk.Button(
            label="Add",
            image=Gtk.Image.new_from_icon_name("list-add", 0),
            always_show_image=True,
        )
        addBtn.connect("clicked", self.on_addBtn_clicked)

        super().__init__(trust_func, self.__status_markup, addBtn)

    def __status_markup(self, status):
        s = status.lower()
        return (
            ("<b><u>T</u></b>/D", Colors.LIGHT_GREEN)
            if s == "t"
            else ("T/<b><u>D</u></b>", Colors.LIGHT_RED)
            if s == "d"
            else ("T/D", Colors.LIGHT_YELLOW)
        )

    def _changesets_to_map(self):
        def reducer(map, path):
            map.get(changesetMap[path], []).append(path)
            return map

        # map change path to action, the action for the last change in the queue wins
        changesetMap = {
            path: action
            for e in stateManager.get_changeset_q() or []
            for (path, action) in e.get_path_action_map().items()
        }
        return reduce(
            reducer,
            changesetMap,
            {"Add": [], "Del": []},
        )

    def _columns(self):
        statusColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_CHANGES_HEADER,
            Gtk.CellRendererText(background="light gray"),
            text=4,
        )
        statusColumn.set_sort_column_id(4)
        return [statusColumn, *super()._columns()]

    def load_trust(self, trust):
        changesetMap = self._changesets_to_map()

        store = Gtk.ListStore(str, str, object, str, str)
        for i, data in enumerate(trust):
            status, *rest = self.markup_func(data.status)
            bgColor = rest[0] if rest else "white"
            changes = (
                strings.CHANGESET_ACTION_ADD if data.path in changesetMap["Add"] else ""
            )
            store.append([status, data.path, data, bgColor, changes])

        for pth in changesetMap["Del"]:
            store.append(
                [
                    "T/D",
                    pth,
                    SimpleNamespace(path=pth),
                    "white",
                    strings.CHANGESET_ACTION_DEL,
                ]
            )

        self.load_store(store)

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
