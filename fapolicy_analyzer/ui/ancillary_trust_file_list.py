import gi
import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from functools import reduce
from gi.repository import Gtk
from types import SimpleNamespace
from time import localtime, strftime
from .configs import Colors
from .add_file_button import AddFileButton
from .state_manager import stateManager
from .trust_file_list import TrustFileList


class AncillaryTrustFileList(TrustFileList):
    def __init__(self, trust_func):
        addBtn = AddFileButton()
        addBtn.files_added += self.on_addBtn_files_added
        self.changesColumn = None

        super().__init__(trust_func, self.__status_markup, addBtn.get_ref())

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
            p: a
            for e in stateManager.get_changeset_q() or []
            for (p, a) in e.get_path_action_map().items()
        }
        return reduce(
            reducer,
            changesetMap,
            {"Add": [], "Del": []},
        )

    def _columns(self):
        self.changesColumn = Gtk.TreeViewColumn(
            strings.FILE_LIST_CHANGES_HEADER,
            Gtk.CellRendererText(background="light gray"),
            text=4,
        )
        self.changesColumn.set_sort_column_id(4)
        return [self.changesColumn, *super()._columns()]

    def load_trust(self, trust):
        changesetMap = self._changesets_to_map()

        # Hide changes column if there are no changes
        self.changesColumn.set_visible(changesetMap["Add"] or changesetMap["Del"])

        store = Gtk.ListStore(str, str, str, object, str, str)
        for i, data in enumerate(trust):
            status, *rest = self.markup_func(data.status)
            bgColor = rest[0] if rest else "white"
            changes = (
                strings.CHANGESET_ACTION_ADD if data.path in changesetMap["Add"] else ""
            )
            strDateTime = (
                strftime("%Y-%m-%d %H:%M:%S", localtime(data.actual.last_modified))
                if data.actual
                else "Missing"
            )
            store.append([status, strDateTime, data.path, data, bgColor, changes])

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

    def on_addBtn_files_added(self, files):
        if files:
            self.files_added(files)
