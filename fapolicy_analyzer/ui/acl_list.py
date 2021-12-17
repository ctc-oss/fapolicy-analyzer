# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .searchable_list import SearchableList


class ACLList(SearchableList):
    def __init__(self, label="User", label_plural=None):
        super().__init__(self.__columns(), view_headers_visible=False)

        self.label = label
        self.label_plural = (
            f"{label}s" if label_plural is None and label is not None else label_plural
        )

    def __columns(self):
        return [Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=0)]

    def _update_tree_count(self, count):
        lbl = self.label if count == 1 else self.label_plural
        self.treeCount.set_text(" ".join([str(count), lbl or ""]).strip())

    def load_store(self, acls, **kwargs):
        store = Gtk.ListStore(str, int)

        for acl in acls:
            store.append([acl.get("name"), acl.get("id")])

        super().load_store(store)
