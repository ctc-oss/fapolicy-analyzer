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
from fapolicy_analyzer.ui.actions import (
    ADD_NOTIFICATION,
    APPLY_CHANGESETS,
    MODIFY_RULES_TEXT,
    NotificationType,
)
from fapolicy_analyzer.ui.changeset_wrapper import RuleChangeset
from fapolicy_analyzer.ui.rules import RulesAdminPage
from fapolicy_analyzer.ui.store import init_store
from fapolicy_analyzer.ui.strings import (
    APPLY_CHANGESETS_ERROR_MESSAGE,
    RULES_LOAD_ERROR,
    RULES_TEXT_LOAD_ERROR,
)
from mocks import mock_rule, mock_System
from fapolicy_analyzer.redux import Action
from rx.subject import Subject

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.rules.rules_admin_page.dispatch")


@pytest.fixture()
def mock_system_feature(mocker):
    mockSystemFeature = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_admin_page.get_system_feature",
        return_value=mockSystemFeature,
    )
    yield mockSystemFeature
    mockSystemFeature.on_completed()


@pytest.fixture
def widget(mock_dispatch, mock_system_feature):
    init_store(mock_System())
    return RulesAdminPage()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Paned


def test_populates_guided_editor(widget, mock_system_feature, mocker):
    mock_rules = [mock_rule()]
    mock_list_renderer = MagicMock()
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_list_view.RulesListView.render_rules",
        mock_list_renderer,
    )
    mock_system_feature.on_next(
        {
            "rules": MagicMock(error=None, rules=mock_rules, loading=False),
            "rules_text": MagicMock(),
            "changesets": MagicMock(),
        }
    )
    mock_list_renderer.assert_called_once_with(mock_rules)


@pytest.mark.usefixtures("widget")
def test_populates_status_info(mock_system_feature, mocker):
    mock_rules = [
        MagicMock(
            id=1,
            text="Mock Rule Number 1",
            is_valid=True,
            info=[MagicMock(category="i", message="info message")],
        ),
        MagicMock(
            id=1,
            text="Mock Rule Number 1",
            is_valid=False,
            info=[
                MagicMock(category="w", message="warning message"),
                MagicMock(category="i", message="other info"),
            ],
        ),
    ]
    mock_info_renderer = MagicMock()
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_status_info.RulesStatusInfo.render_rule_status",
        mock_info_renderer,
    )
    mock_system_feature.on_next(
        {
            "rules": MagicMock(error=None, rules=mock_rules, loading=False),
            "rules_text": MagicMock(),
            "changesets": MagicMock(),
        }
    )
    mock_info_renderer.assert_called_once_with(mock_rules)


@pytest.mark.usefixtures("widget")
def test_handles_rules_exception(mock_dispatch, mock_system_feature):
    mock_dispatch.reset_mock()
    mock_system_feature.on_next(
        {
            "rules": MagicMock(error="foo", loading=False),
            "rules_text": MagicMock(),
            "changesets": MagicMock(),
        }
    )
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(text=RULES_LOAD_ERROR),
        )
    )


@pytest.mark.usefixtures("widget")
def test_populates_text_editor(mock_system_feature, mocker):
    mock_text_renderer = MagicMock()
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_text_view.RulesTextView.render_rules",
        mock_text_renderer,
    )
    mock_system_feature.on_next(
        {
            "rules": MagicMock(),
            "rules_text": MagicMock(
                error=None,
                rules_text="foo",
                loading=False,
            ),
            "changesets": MagicMock(),
        }
    )
    mock_text_renderer.assert_called_once_with("foo")


@pytest.mark.usefixtures("widget")
def test_handles_rules_text_exception(mock_dispatch, mock_system_feature):
    mock_dispatch.reset_mock()
    mock_system_feature.on_next(
        {
            "rules": MagicMock(),
            "rules_text": MagicMock(error="foo", loading=False),
            "changesets": MagicMock(),
        }
    )
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(text=RULES_TEXT_LOAD_ERROR),
        )
    )


def test_handles_rule_text_change(widget, mock_dispatch):
    widget._text_view.rules_changed("new rules")
    mock_dispatch.assert_called_with(
        InstanceOf(Action) & Attrs(type=MODIFY_RULES_TEXT, payload="new rules")
    )


def test_save_click(widget, mock_dispatch):
    widget._text_view.rules_changed("modified rules")
    widget.on_save_clicked()
    mock_dispatch.assert_called_with(InstanceOf(Action) & Attrs(type=APPLY_CHANGESETS))


def test_apply_changeset_error(mock_dispatch, mocker):
    mockSystemFeature = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_admin_page.get_system_feature",
        return_value=mockSystemFeature,
    )
    mockSystemFeature.on_next(
        {"changesets": MagicMock(spec=RuleChangeset, changesets=[], error=False)}
    )
    init_store(mock_System())
    widget = RulesAdminPage()
    widget.on_save_clicked()  # need to set the saving flag to true

    mockSystemFeature.on_next(
        {
            "changesets": MagicMock(
                spec=RuleChangeset, changesets=[MagicMock()], error="bad error"
            ),
            "rules": MagicMock(loading=True),
            "rules_text": MagicMock(loading=True),
        }
    )
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(
                type=NotificationType.ERROR, text=APPLY_CHANGESETS_ERROR_MESSAGE
            ),
        )
    )
