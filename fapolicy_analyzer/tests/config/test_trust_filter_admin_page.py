# Copyright Concurrent Technologies Corporation 2024
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
from mocks import mock_System
from rx.subject import Subject

from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import (
    ADD_NOTIFICATION,
    APPLY_CHANGESETS,
    MODIFY_CONFIG_TEXT,
    NotificationType,
)
from fapolicy_analyzer.ui.config.config_admin_page import ConfigAdminPage
from fapolicy_analyzer.ui.store import init_store
from fapolicy_analyzer.ui.strings import (
    TRUST_FILTER_TEXT_LOAD_ERROR,
    TRUST_FILTER_CHANGESET_PARSE_ERROR,
)


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip

initial_system = {
    "config_text": MagicMock(error=None, loading=False, config_text=""),
    "changesets": MagicMock(),
    "system": MagicMock(),
}


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.config.config_admin_page.dispatch")


@pytest.fixture()
def mock_system_feature(mocker):
    mockSystemFeature = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.config.config_admin_page.get_system_feature",
        return_value=mockSystemFeature,
    )
    yield mockSystemFeature
    mockSystemFeature.on_completed()


@pytest.fixture
def widget(mock_dispatch, mock_system_feature):
    init_store(mock_System())
    return ConfigAdminPage()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Paned


@pytest.mark.usefixtures("widget")
def test_populates_text_editor(mock_system_feature, mocker):
    mock_text_renderer = MagicMock()
    mocker.patch(
        "fapolicy_analyzer.ui.config.config_admin_page.ConfigTextView.render_text",
        mock_text_renderer,
    )
    mock_system_feature.on_next(
        {
            **initial_system,
            "config_text": MagicMock(
                error=None,
                config_text="foo",
                loading=False,
            ),
        }
    )
    mock_text_renderer.assert_called_once_with("foo")


@pytest.mark.usefixtures("widget")
def test_handles_config_text_exception(mock_dispatch, mock_system_feature):
    mock_dispatch.reset_mock()
    mock_system_feature.on_next(
        {
            **initial_system,
            "config_text": MagicMock(error="foo", loading=False),
        }
    )
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(text=CONFIG_TEXT_LOAD_ERROR),
        )
    )


def test_handles_config_text_change(widget, mock_dispatch):
    widget._text_view.config_changed("new config")
    mock_dispatch.assert_called_with(
        InstanceOf(Action) & Attrs(type=MODIFY_CONFIG_TEXT, payload="new config")
    )


def test_save_click_valid(widget, mock_dispatch):
    widget._text_view.config_changed("permissive = 1")
    widget.on_save_clicked()
    mock_dispatch.assert_called_with(InstanceOf(Action) & Attrs(type=APPLY_CHANGESETS))


def test_save_click_invalid(widget, mock_dispatch, mocker):
    widget._text_view.config_changed("permissive = foo")
    overrideDialog = widget.get_object("saveOverrideDialog")
    mocker.patch.object(overrideDialog, "run", return_value=Gtk.ResponseType.CANCEL)
    widget.on_save_clicked()
    mock_dispatch.assert_not_any_call(InstanceOf(Action) & Attrs(type=APPLY_CHANGESETS))


def test_validate_clicked_valid(widget, mock_dispatch):
    widget._text_view.config_changed("permissive = 1")
    widget.on_validate_clicked()
    mock_dispatch.assert_not_any_call(InstanceOf(Action) & Attrs(type=ADD_NOTIFICATION))


def test_validate_clicked_invalid(widget, mock_dispatch):
    widget._text_view.config_changed("permissive = foo")
    widget.on_validate_clicked()
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(
                type=NotificationType.ERROR, text=CONFIG_CHANGESET_PARSE_ERROR
            ),
        )
    )
