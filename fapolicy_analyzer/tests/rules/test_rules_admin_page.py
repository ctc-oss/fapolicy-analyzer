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
from mocks import mock_rule, mock_System
from rx.subject import Subject

from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import (
    ADD_NOTIFICATION,
    APPLY_CHANGESETS,
    MODIFY_RULES_TEXT,
    REMOVE_NOTIFICATION,
    Notification,
    NotificationType,
)
from fapolicy_analyzer.ui.changeset_wrapper import RuleChangeset
from fapolicy_analyzer.ui.rules import RulesAdminPage
from fapolicy_analyzer.ui.store import init_store
from fapolicy_analyzer.ui.strings import (
    APPLY_CHANGESETS_ERROR_MESSAGE,
    RULES_CHANGESET_PARSE_ERROR,
    RULES_LOAD_ERROR,
    RULES_TEXT_LOAD_ERROR,
    RULES_VALIDATION_ERROR,
    RULES_VALIDATION_WARNING,
)

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip

initial_system = {
    "rules": MagicMock(error=None, rules=[], loading=False),
    "rules_text": MagicMock(error=None, loading=False, rules_text=""),
    "changesets": MagicMock(),
    "system": MagicMock(),
}


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
def mock_notifications_feature(mocker):
    notifications_feature_mock = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_admin_page.get_notifications_feature",
        return_value=notifications_feature_mock,
    )
    yield notifications_feature_mock
    notifications_feature_mock.on_completed()


@pytest.fixture
def widget(mock_dispatch, mock_system_feature, mock_notifications_feature):
    init_store(mock_System())
    return RulesAdminPage()


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Paned


@pytest.mark.usefixtures("mock_system_feature")
def test_disposes(mocker):
    mockDispose = MagicMock()
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_admin_page.get_notifications_feature",
        return_value=MagicMock(
            subscribe=MagicMock(return_value=MagicMock(dispose=mockDispose))
        ),
    )
    widget = RulesAdminPage()
    widget.dispose()
    mockDispose.assert_called_once()


def test_populates_guided_editor(widget, mock_system_feature, mocker):
    mock_rules = [mock_rule()]
    mock_list_renderer = MagicMock()
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_admin_page.RulesListView.render_rules",
        mock_list_renderer,
    )
    mock_system_feature.on_next(
        {
            **initial_system,
            "rules": MagicMock(error=None, rules=mock_rules, loading=False),
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
        "fapolicy_analyzer.ui.rules.rules_admin_page.RulesStatusInfo.render_rule_status",
        mock_info_renderer,
    )
    mock_system_feature.on_next(
        {
            **initial_system,
            "rules": MagicMock(error=None, rules=mock_rules, loading=False),
        }
    )
    mock_info_renderer.assert_called_once_with(mock_rules)


@pytest.mark.usefixtures("widget")
def test_handles_rules_exception(mock_dispatch, mock_system_feature):
    mock_dispatch.reset_mock()
    mock_system_feature.on_next(
        {
            **initial_system,
            "rules": MagicMock(error="foo", loading=False),
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
        "fapolicy_analyzer.ui.rules.rules_admin_page.RulesTextView.render_rules",
        mock_text_renderer,
    )
    mock_system_feature.on_next(
        {
            **initial_system,
            "rules_text": MagicMock(
                error=None,
                rules_text="foo",
                loading=False,
            ),
        }
    )
    mock_text_renderer.assert_called_once_with("foo")


@pytest.mark.usefixtures("widget")
def test_handles_rules_text_exception(mock_dispatch, mock_system_feature):
    mock_dispatch.reset_mock()
    mock_system_feature.on_next(
        {
            **initial_system,
            "rules_text": MagicMock(error="foo", loading=False),
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


def test_validate_clicked_valid(widget, mock_dispatch):
    widget._text_view.rules_changed("allow perm=open all : all")
    widget.on_validate_clicked()
    mock_dispatch.assert_not_any_call(InstanceOf(Action) & Attrs(type=ADD_NOTIFICATION))


def test_validate_clicked_invalid(widget, mock_dispatch):
    widget._text_view.rules_changed("bar baz bah")
    widget.on_validate_clicked()
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(type=NotificationType.ERROR, text=RULES_VALIDATION_ERROR),
        )
    )


def test_validate_clicked_warning(widget, mock_dispatch):
    widget._text_view.rules_changed("allow perm=any exe=/foo : all")
    widget.on_validate_clicked()
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(type=NotificationType.WARN, text=RULES_VALIDATION_WARNING),
        )
    )


def test_clears_validation_notifications(
    widget, mock_notifications_feature, mock_dispatch
):
    mock_notifications_feature.on_next(
        [Notification(0, "error", NotificationType.ERROR, "invalid rules")]
    )
    # valid to clear notification
    widget._text_view.rules_changed("allow perm=open all : all")
    widget.on_validate_clicked()
    print(mock_dispatch.call_args_list)
    mock_dispatch.assert_any_call(
        InstanceOf(Action)
        & Attrs(
            type=REMOVE_NOTIFICATION,
            payload=Notification(id=0, text="", type=None, category=None),
        )
    )


def test_validate_updates_rules_list(widget, mock_system_feature, mocker):
    mock_list_renderer = MagicMock()
    mock_system = MagicMock(rules=MagicMock(return_value="parsed rules"))
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_admin_page.RulesListView.render_rules",
        mock_list_renderer,
    )
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_admin_page.RuleChangeset.apply_to_system",
        return_value=mock_system,
    )
    mock_system_feature.on_next(initial_system)
    widget._text_view.rules_changed("allow perm=open all : all")
    widget.on_validate_clicked()
    mock_list_renderer.assert_called_with("parsed rules")


def test_handles_rules_parsing_failure(widget, mock_system_feature, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_admin_page.RuleChangeset.apply_to_system",
        side_effect=Exception,
    )
    mock_logger = mocker.patch("fapolicy_analyzer.ui.rules.rules_admin_page.logging")
    mock_system_feature.on_next(initial_system)
    widget._text_view.rules_changed("allow perm=open all : all")
    widget.on_validate_clicked()
    mock_logger.warning.assert_called_with("Failed to parse validating changeset")


def test_save_click_valid(widget, mock_dispatch):
    widget._text_view.rules_changed("allow perm=any all : all")
    widget.on_save_clicked()
    mock_dispatch.assert_called_with(InstanceOf(Action) & Attrs(type=APPLY_CHANGESETS))


def test_save_click_invalid(widget, mock_dispatch):
    widget._text_view.rules_changed("bar baz bah")
    widget.on_save_clicked()
    mock_dispatch.assert_not_any_call(InstanceOf(Action) & Attrs(type=APPLY_CHANGESETS))


def test_changeset_parse_error(widget, mock_dispatch, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.rules.rules_admin_page.RuleChangeset.parse",
        side_effect=Exception,
    )
    widget._text_view.rules_changed("allow perm=any all : all")
    widget.on_save_clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(
                type=NotificationType.ERROR, text=RULES_CHANGESET_PARSE_ERROR
            ),
        )
    )
    mock_dispatch.assert_not_any_call(InstanceOf(Action) & Attrs(type=APPLY_CHANGESETS))


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
    widget._text_view.rules_changed("allow perm=any all : all")
    widget.on_save_clicked()  # need to set the saving flag to true

    mockSystemFeature.on_next(
        {
            **initial_system,
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


def test_forces_rule_text_update_after_save(widget, mock_dispatch, mock_system_feature):
    def assert_text(expected):
        assert (
            buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
            == expected
        )

    text_view = widget._text_view
    buffer = text_view.get_object("textView").get_buffer()
    original_text = "allow perm=any all : all"

    mock_system_feature.on_next(
        {
            **initial_system,
            "rules_text": MagicMock(
                error=None, loading=False, rules_text=original_text
            ),
        }
    )

    assert_text(original_text)

    # insert single trailing space
    buffer.insert(buffer.get_end_iter(), " ", 1)
    assert_text(original_text + " ")

    widget.on_save_clicked()

    # when the rules text is retrieved again from rust the trailing space will be stripped
    mock_system_feature.on_next(
        {
            **initial_system,
            "changesets": MagicMock(
                spec=RuleChangeset, changesets=[MagicMock()], error=None
            ),
            "rules_text": MagicMock(
                error=None, loading=False, rules_text=original_text
            ),
        }
    )
    assert_text(original_text)


def test_preserve_list_row_collapse(widget):
    mock_rules = [
        MagicMock(
            id=1,
            text="Mock Rule Number 1",
            is_valid=True,
            origin="Rule File 1",
            info=[],
        ),
        MagicMock(
            id=2,
            text="Mock Rule Number 2",
            origin="Rule File 1",
            is_valid=True,
            info=[MagicMock(category="i", message="info message")],
        ),
    ]
    widget._list_view.render_rules(mock_rules)
    model = widget._list_view.get_object("treeView").get_model()
    iter = model.get_iter_first()
    assert widget._list_view.treeView.row_expanded(model.get_path(iter)) is True
    widget._list_view.treeView.collapse_row(model.get_path(iter))
    widget._text_view.rules_changed("allow perm=any exe=/foo : all")
    widget.on_validate_clicked()
    iter = model.get_iter_first()
    assert widget._list_view.treeView.row_expanded(model.get_path(iter)) is False
