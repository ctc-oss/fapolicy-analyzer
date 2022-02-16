# Copyright Concurrent Technologies Corporation 2022
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

import context  # noqa: F401 # isort: skip
from unittest.mock import MagicMock

import gi
import pytest
from callee import Attrs, InstanceOf
from fapolicy_analyzer.ui.rules import RulesAdminPage
from redux import Action
from rx.subject import Subject
from ui.actions import ADD_NOTIFICATION
from ui.store import init_store
from ui.strings import RULES_LOAD_ERROR

from mocks import mock_rule, mock_System

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("ui.rules_admin_page.dispatch")


@pytest.fixture()
def mock_system_feature(mocker):
    mockSystemFeature = Subject()
    mocker.patch(
        "ui.rules_admin_page.get_system_feature",
        return_value=mockSystemFeature,
    )
    yield mockSystemFeature
    mockSystemFeature.on_completed()


@pytest.fixture
def widget(mock_dispatch, mock_system_feature):
    init_store(mock_System())
    return RulesAdminPage()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Notebook


def test_populates_rules(widget, mock_system_feature):
    mock_system_feature.on_next(
        {
            "rules": MagicMock(error=None, rules=[mock_rule()], loading=False),
        }
    )
    textView = widget.get_object("legacyTextView")
    textBuffer = textView.get_buffer()
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == mock_rule().text
    )


@pytest.mark.usefixtures("widget")
def test_rules_w_exception(mock_dispatch, mock_system_feature):
    mock_dispatch.reset_mock()
    mock_system_feature.on_next({"rules": MagicMock(error="foo", loading=False)})
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(text=RULES_LOAD_ERROR),
        )
    )
