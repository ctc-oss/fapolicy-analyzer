# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from time import localtime, mktime, strftime
from unittest.mock import MagicMock

from gi.repository import Gtk
from helpers import refresh_gui

from fapolicy_analyzer.ui.trust_file_list import TrustFileList, epoch_to_string

_trust = [
    MagicMock(status="u", path="/tmp/bar", actual=MagicMock(last_modified=123456789)),
    MagicMock(status="t", path="/tmp/foo", actual=MagicMock(last_modified=123456789)),
]


@pytest.fixture
def widget():
    widget = TrustFileList(trust_func=MagicMock())
    return widget


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_uses_custom_trust_func():
    trust_func = MagicMock()
    TrustFileList(trust_func=trust_func)
    trust_func.assert_called()


def test_uses_custom_markup_func(mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.trust_file_list.ThreadPoolExecutor",
        return_value=MagicMock(submit=lambda x, *args: x(*args)),
    )
    markup_func = MagicMock(return_value="t")
    widget = TrustFileList(trust_func=MagicMock(), markup_func=markup_func)
    widget.init_list(2)
    widget.append_trust(_trust)
    markup_func.assert_called_with("t")


def test_loads_trust_store(widget, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.trust_file_list.ThreadPoolExecutor",
        return_value=MagicMock(submit=lambda x: x()),
    )
    mocker.patch(
        "fapolicy_analyzer.ui.trust_file_list.GLib.idle_add",
        side_effect=lambda x, args: x(args),
    )
    widget.init_list(2)
    widget.append_trust(_trust)
    refresh_gui(delay=0.5)
    view = widget.get_object("treeView")
    assert [t.status for t in _trust] == [x[0] for x in view.get_model()]
    assert [t.path for t in _trust] == [x[2] for x in view.get_model()]


def test_cancels_load_trust_store(widget, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.trust_file_list.ThreadPoolExecutor",
        return_value=MagicMock(submit=lambda x: x()),
    )
    mockIdleAdd = mocker.patch("fapolicy_analyzer.ui.trust_file_list.GLib.idle_add")
    widget.init_list(2)
    # trust_file_list._executorCanceled = True
    widget.on_destroy()

    widget.append_trust(_trust)
    refresh_gui(delay=0.5)
    mockIdleAdd.assert_not_called()


def test_fires_trust_selection_changed(widget):
    store = Gtk.ListStore(str, str, str, object, str)
    store.append(["f", "o", "o", _trust[0], "baz"])
    widget.load_store(1, store)
    mockHandler = MagicMock()
    widget.trust_selection_changed += mockHandler
    view = widget.get_object("treeView")
    view.get_selection().select_path(Gtk.TreePath.new_first())
    mockHandler.assert_called_with([_trust[0]])


def test_epoch_to_string():
    secsEpochCurrent = int(mktime(localtime()))
    secsEpochOneDayOld = secsEpochCurrent - (24 * 60 * 60)

    # Verify timestamps from today are display in hour:minute:sec format
    strExpected = strftime("%H:%M:%S", localtime(secsEpochCurrent))
    strFromEpochToString = epoch_to_string(secsEpochCurrent)
    assert strExpected == strFromEpochToString

    # Verify timestamps older than today are displayed as calendar date
    strExpected = strftime("%Y-%m-%d", localtime(secsEpochOneDayOld))
    strFromEpochToString = epoch_to_string(secsEpochOneDayOld)
    assert strExpected == strFromEpochToString

    # Verify a NULL string input outputs "Missing"
    assert epoch_to_string(None) == "Missing"
