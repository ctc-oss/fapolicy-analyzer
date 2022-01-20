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

import gi
import pytest

import context  # noqa: F401

gi.require_version("Gtk", "3.0")
from unittest.mock import MagicMock

from callee import Attrs, InstanceOf
from gi.repository import Gtk
from redux import Action
from rx.subject import Subject
from ui.actions import (
    ADD_NOTIFICATION,
    REQUEST_EVENTS,
    REQUEST_GROUPS,
    REQUEST_USERS,
    NotificationType,
)
from ui.policy_rules_admin_page import PolicyRulesAdminPage
from ui.store import init_store
from ui.strings import (
    GET_GROUPS_LOG_ERROR_MSG,
    GET_USERS_ERROR_MSG,
    PARSE_EVENT_LOG_ERROR_MSG,
)

from mocks import mock_events, mock_groups, mock_log, mock_System, mock_users

_mock_file = "foo"


def _build_state(**kwargs):
    initial_state = {
        "events": {"loading": False, "error": None, "events": []},
        "groups": {"loading": False, "error": None, "groups": []},
        "users": {"loading": False, "error": None, "users": []},
        "system_trust": {"loading": False, "error": None, "trust": []},
        "ancillary_trust": {"loading": False, "error": None, "trust": []},
    }

    combined = {
        **initial_state,
        **{k: {**initial_state.get(k, {}), **v} for k, v in kwargs.items()},
    }
    return {k: MagicMock(**v) for k, v in combined.items()}


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("ui.policy_rules_admin_page.dispatch")


@pytest.fixture()
def mock_system_features(mocker):
    system_features_mock = Subject()
    mocker.patch(
        "ui.policy_rules_admin_page.get_system_feature",
        return_value=system_features_mock,
    )
    yield system_features_mock
    system_features_mock.on_completed()


@pytest.fixture(name="states")
def default_states():
    """
    Work around for the fact that parameterized arguments of a fixture cannot have default values.
    Used in the widget fixture to provide a default for the states argument.
    """
    return [
        _build_state(
            events={"log": mock_log()},
            groups={"groups": mock_groups()},
            users={"users": mock_users()},
        )
    ]


@pytest.fixture
def widget(mock_dispatch, mock_system_features, mocker, states):
    mocker.patch(
        "ui.ancillary_trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    mocker.patch(
        "ui.trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    init_store(mock_System())
    widget = PolicyRulesAdminPage(_mock_file)

    for s in states:
        mock_system_features.on_next(s)

    return widget


@pytest.fixture
def userListView(widget):
    return widget.user_list.get_object("treeView")


@pytest.fixture
def groupListView(widget):
    return widget.group_list.get_object("treeView")


@pytest.fixture
def subjectListView(widget):
    return widget.subject_list.get_object("treeView")


@pytest.fixture
def objectListView(widget):
    return widget.object_list.get_object("treeView")


@pytest.fixture
def activeSwitcherButton(widget):
    # find switcher button, either the 1st button in the user list
    # or 2nd button in subject list. Only 1 should exist at any point in time.
    return next(
        iter(
            [
                *widget.user_list.get_action_buttons()[0:],
                *widget.subject_list.get_action_buttons()[1:],
            ]
        )
    )


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def test_loads_debug_file(mock_dispatch):
    init_store(mock_System())
    PolicyRulesAdminPage(_mock_file)
    mock_dispatch.assert_any_call(
        InstanceOf(Action) & Attrs(type=REQUEST_EVENTS, payload=("debug", _mock_file))
    )


def test_loads_syslog(mock_dispatch):
    init_store(mock_System())
    PolicyRulesAdminPage()
    mock_dispatch.assert_any_call(
        InstanceOf(Action) & Attrs(type=REQUEST_EVENTS, payload=("syslog", None))
    )


def test_adds_user_tabs(widget):
    tabs = widget.get_object("userTabs")
    page = tabs.get_nth_page(0)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "User"
    page = tabs.get_nth_page(1)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "Group"
    page = tabs.get_nth_page(2)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "All"


def test_adds_subject_tabs(widget):
    tabs = widget.get_object("subjectTabs")
    page = tabs.get_nth_page(0)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "Subject"


def test_adds_object_tabs(widget):
    tabs = widget.get_object("objectTabs")
    page = tabs.get_nth_page(0)
    assert type(page) is Gtk.Box
    assert tabs.get_tab_label_text(page) == "Object"


def test_switches_acl_subject_columns(widget, activeSwitcherButton):
    aclColumn = widget.get_object("userPanel")
    subjectColumn = widget.get_object("subjectPanel")
    children = widget.get_ref().get_children()
    assert children[0] == aclColumn
    assert children[1] == subjectColumn
    activeSwitcherButton.clicked()
    children = widget.get_ref().get_children()
    assert children[0] == subjectColumn
    assert children[1] == aclColumn


def test_loads_users_primary(userListView, mock_dispatch):
    model = userListView.get_model()
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=REQUEST_USERS))
    assert len(model) == 2
    assert [x.name for x in mock_users()] == [x[0] for x in model]
    assert [x.id for x in mock_users()] == [x[1] for x in model]


def test_loads_groups_primary(groupListView, mock_dispatch):
    model = groupListView.get_model()
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=REQUEST_GROUPS))
    assert len(model) == 2
    assert [x.name for x in mock_groups()] == [x[0] for x in model]
    assert [x.id for x in mock_groups()] == [x[1] for x in model]


def test_loads_subjects_primary(subjectListView, activeSwitcherButton, mock_dispatch):
    activeSwitcherButton.clicked()
    model = subjectListView.get_model()
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=REQUEST_EVENTS))
    expectedSubjects = [e.subject for e in mock_events()]
    assert len(model) == 2
    for idx, expectedSubject in enumerate(expectedSubjects):
        assert expectedSubject.trust in model[idx][0]
        assert expectedSubject.access in model[idx][1]
        assert expectedSubject.file == model[idx][2]


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_loads_subjects_secondary(view, subjectListView, mock_dispatch):
    view.get_selection().select_path(Gtk.TreePath.new_first())
    model = subjectListView.get_model()
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=REQUEST_EVENTS))
    expectedSubject = mock_events()[0].subject
    assert len(model) == 1
    assert expectedSubject.trust in next(iter([x[0] for x in model]))
    assert expectedSubject.access in next(iter([x[1] for x in model]))
    assert expectedSubject.file == next(iter([x[2] for x in model]))


def test_loads_users_secondary(
    userListView, activeSwitcherButton, subjectListView, mock_dispatch
):
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=REQUEST_USERS))
    activeSwitcherButton.clicked()
    model = userListView.get_model()
    assert len(model) == 0

    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    model = userListView.get_model()
    expectedUser = mock_users()[0]
    assert len(model) == 1
    assert expectedUser.name == next(iter([x[0] for x in model]))
    assert expectedUser.id == next(iter([x[1] for x in model]))


def test_loads_groups_secondary(
    groupListView, activeSwitcherButton, subjectListView, mock_dispatch
):
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=REQUEST_GROUPS))
    activeSwitcherButton.clicked()
    model = groupListView.get_model()
    assert len(model) == 0

    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    model = groupListView.get_model()
    expectedGroup = mock_groups()[0]
    assert len(model) == 1
    assert expectedGroup.name == next(iter([x[0] for x in model]))
    assert expectedGroup.id == next(iter([x[1] for x in model]))


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_loads_objects_from_subject(view, subjectListView, objectListView):
    view.get_selection().select_path(Gtk.TreePath.new_first())
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    model = objectListView.get_model()
    expectedObject = mock_events()[0].object
    assert expectedObject.trust in next(iter([x[0] for x in model]))
    assert expectedObject.access in next(iter([x[1] for x in model]))
    assert expectedObject.file == next(iter([x[2] for x in model]))
    assert expectedObject.mode in next(iter([x[5] for x in model]))


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_loads_objects_from_acl(
    view, subjectListView, objectListView, activeSwitcherButton
):
    activeSwitcherButton.clicked()
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    view.get_selection().select_path(Gtk.TreePath.new_first())
    model = objectListView.get_model()
    expectedObject = mock_events()[0].object
    assert expectedObject.trust in next(iter([x[0] for x in model]))
    assert expectedObject.access in next(iter([x[1] for x in model]))
    assert expectedObject.file == next(iter([x[2] for x in model]))
    assert expectedObject.mode in next(iter([x[5] for x in model]))


@pytest.mark.parametrize(
    "view, mockFnName",
    [
        (pytest.lazy_fixture("userListView"), "getUserDetails"),
        (pytest.lazy_fixture("groupListView"), "getGroupDetails"),
    ],
)
def test_updates_acl_details(widget, view, mockFnName, mocker):
    mocker.patch(f"ui.policy_rules_admin_page.acl.{mockFnName}", return_value="foo")
    textBuffer = widget.get_object("userDetails").get_buffer()
    view.get_selection().select_path(Gtk.TreePath.new_first())
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_updates_subject_details(widget, mocker):
    mocker.patch("ui.policy_rules_admin_page.fs.stat", return_value="foo")
    textBuffer = widget.get_object("subjectDetails").get_buffer()
    widget.on_subject_selection_changed(MagicMock(), MagicMock(file="baz"))
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_updates_object_details(widget, mocker):
    mocker.patch("ui.policy_rules_admin_page.fs.stat", return_value="foo")
    textBuffer = widget.get_object("objectDetails").get_buffer()
    widget.on_object_selection_changed(MagicMock(file="baz"))
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_handles_empty_acl_select(widget, view, subjectListView):
    view.get_selection().select_path(Gtk.TreePath.new_first())
    assert widget.subject_list.get_ref().get_sensitive()
    assert len([x for x in subjectListView.get_model()]) > 0
    view.get_selection().unselect_all()
    textBuffer = widget.get_object("userDetails").get_buffer()
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == ""
    )
    assert not widget.subject_list.get_ref().get_sensitive()
    assert len([x for x in subjectListView.get_model()]) == 0


def test_handles_empty_subject_select(
    widget, userListView, subjectListView, objectListView
):
    userListView.get_selection().select_path(Gtk.TreePath.new_first())
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    textBuffer = widget.get_object("subjectDetails").get_buffer()
    assert (
        len(
            textBuffer.get_text(
                textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
            )
        )
        != 0
    )
    assert widget.object_list.get_ref().get_sensitive()
    assert len([x for x in objectListView.get_model()]) > 0

    subjectListView.get_selection().unselect_all()
    assert (
        len(
            textBuffer.get_text(
                textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
            )
        )
        == 0
    )
    assert not widget.object_list.get_ref().get_sensitive()
    assert len([x for x in objectListView.get_model()]) == 0


def test_handles_empty_object_select(
    widget, userListView, subjectListView, objectListView
):
    userListView.get_selection().select_path(Gtk.TreePath.new_first())
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    objectListView.get_selection().select_path(Gtk.TreePath.new_first())
    textBuffer = widget.get_object("objectDetails").get_buffer()
    assert (
        len(
            textBuffer.get_text(
                textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
            )
        )
        != 0
    )

    subjectListView.get_selection().unselect_all()
    assert (
        len(
            textBuffer.get_text(
                textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
            )
        )
        == 0
    )


def test_clears_selection_when_switching_acl_tabs(widget, userListView, groupListView):
    tabs = widget.get_object("userTabs")
    userSelection = userListView.get_selection()
    groupSelection = groupListView.get_selection()

    userSelection.select_path(Gtk.TreePath.new_first())
    assert userSelection.count_selected_rows() == 1
    assert groupSelection.count_selected_rows() == 0
    tabs.set_current_page(1)
    groupSelection.select_path(Gtk.TreePath.new_first())
    assert userSelection.count_selected_rows() == 0
    assert groupSelection.count_selected_rows() == 1
    tabs.set_current_page(0)
    userSelection.select_path(Gtk.TreePath.new_first())
    assert userSelection.count_selected_rows() == 1
    assert groupSelection.count_selected_rows() == 0


def test_event_loading_w_exception(mock_system_features, states, mock_dispatch):
    init_store(mock_System())
    PolicyRulesAdminPage(_mock_file)
    mock_system_features.on_next(
        {**states[0], **{"events": MagicMock(error="foo", loading=False)}}
    )
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(type=NotificationType.ERROR, text=PARSE_EVENT_LOG_ERROR_MSG),
        )
    )


def test_users_loading_w_exception(mock_system_features, states, mock_dispatch):
    init_store(mock_System())
    PolicyRulesAdminPage(_mock_file)
    mock_system_features.on_next(
        {**states[0], **{"users": MagicMock(error="foo", loading=False)}}
    )
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(type=NotificationType.ERROR, text=GET_USERS_ERROR_MSG),
        )
    )


def test_groups_loading_w_exception(mock_system_features, states, mock_dispatch):
    init_store(mock_System())
    PolicyRulesAdminPage(_mock_file)
    mock_system_features.on_next(
        {**states[0], **{"groups": MagicMock(error="foo", loading=False)}}
    )
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=ADD_NOTIFICATION,
            payload=Attrs(type=NotificationType.ERROR, text=GET_GROUPS_LOG_ERROR_MSG),
        )
    )
