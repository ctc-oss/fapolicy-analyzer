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

import context  # noqa: F401 # isort: skip
from unittest.mock import MagicMock

import gi
import pytest
from callee import Attrs, InstanceOf
from mocks import mock_events, mock_groups, mock_log, mock_System, mock_users
from rx.subject import Subject

from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import (
    ADD_NOTIFICATION,
    REQUEST_EVENTS,
    REQUEST_GROUPS,
    REQUEST_USERS,
    NotificationType,
)
from fapolicy_analyzer.ui.policy_rules_admin_page import PolicyRulesAdminPage
from fapolicy_analyzer.ui.store import init_store
from fapolicy_analyzer.ui.strings import (
    GET_GROUPS_LOG_ERROR_MSG,
    GET_USERS_ERROR_MSG,
    PARSE_EVENT_LOG_ERROR_MSG,
)

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip

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
    return mocker.patch("fapolicy_analyzer.ui.policy_rules_admin_page.dispatch")


@pytest.fixture()
def mock_system_features(mocker):
    system_features_mock = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.policy_rules_admin_page.get_system_feature",
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
        "fapolicy_analyzer.ui.ancillary_trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    mocker.patch(
        "fapolicy_analyzer.ui.trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    init_store(mock_System())
    widget = PolicyRulesAdminPage(audit_file=_mock_file)

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
    PolicyRulesAdminPage(audit_file=_mock_file)
    mock_dispatch.assert_any_call(
        InstanceOf(Action) & Attrs(type=REQUEST_EVENTS, payload=("debug", _mock_file))
    )


def test_loads_syslog(mock_dispatch):
    init_store(mock_System())
    PolicyRulesAdminPage(use_syslog=True)
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
    children = widget.get_ref().get_children()[1].get_children()[0].get_children()
    assert children[0].get_children()[0] == aclColumn
    assert children[1].get_children()[0] == subjectColumn
    activeSwitcherButton.clicked()
    children = widget.get_ref().get_children()[1].get_children()[0].get_children()
    assert children[0].get_children()[0] == subjectColumn
    assert children[1].get_children()[0] == aclColumn


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
    assert len(model) == 3
    expectedSubjects = [e.subject for e in mock_events()]
    actualSubjects = [(s[0], s[1], s[2]) for s in model]
    for expectedSubject in expectedSubjects:
        assert [a[0] for a in actualSubjects if expectedSubject.trust in a[0]]
        assert [a[1] for a in actualSubjects if expectedSubject.access in a[1]]
        assert [a[2] for a in actualSubjects if expectedSubject.file == a[2]]


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_loads_subjects_secondary(view, subjectListView, mock_dispatch):
    view.get_selection().select_path(Gtk.TreePath.new_first())
    model = subjectListView.get_model()
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=REQUEST_EVENTS))
    assert len(model) == 2
    expectedSubjects = [e.subject for e in mock_events()[0]]
    actualSubjects = [(s[0], s[1], s[2]) for s in model]
    for expectedSubject in expectedSubjects:
        assert [a[0] for a in actualSubjects if expectedSubject.trust in a[0]]
        assert [a[1] for a in actualSubjects if expectedSubject.access in a[1]]
        assert [a[2] for a in actualSubjects if expectedSubject.file == a[2]]


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
    assert len(model) == 1
    expectedObjects = [e.object for e in mock_events()[0]]
    actualObjects = [(o[0], o[1], o[2], o[5]) for o in model]
    for expectedObject in expectedObjects:
        assert [a[0] for a in actualObjects if expectedObject.trust in a[0]]
        assert [a[1] for a in actualObjects if expectedObject.access in a[1]]
        assert [a[2] for a in actualObjects if expectedObject.file == a[2]]
        assert [a[2] for a in actualObjects if expectedObject.mode in a[3]]


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
    assert len(model) == 1
    expectedObjects = [e.object for e in mock_events()[0]]
    actualObjects = [(o[0], o[1], o[2], o[5]) for o in model]
    for expectedObject in expectedObjects:
        assert [a[0] for a in actualObjects if expectedObject.trust in a[0]]
        assert [a[1] for a in actualObjects if expectedObject.access in a[1]]
        assert [a[2] for a in actualObjects if expectedObject.file == a[2]]
        assert [a[2] for a in actualObjects if expectedObject.mode in a[3]]


@pytest.mark.parametrize(
    "aclListView",
    [pytest.lazy_fixture("userListView")],  # , pytest.lazy_fixture("groupListView")],
)
def test_reloads_views_after_refresh(
    aclListView,
    subjectListView,
    objectListView,
    widget,
    mock_dispatch,
    mock_system_features,
    states,
):
    def get_selected_values(view, data_column_num):
        model, paths = view.get_selection().get_selected_rows()
        return [model.get_value(model.get_iter(p), data_column_num) for p in paths]

    aclListView.get_selection().select_path(Gtk.TreePath.new_first())
    prev_selected_acl = get_selected_values(aclListView, 0)
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    prev_selected_subjects = get_selected_values(subjectListView, 2)
    objectListView.get_selection().select_path(Gtk.TreePath.new_first())
    prev_selected_objects = get_selected_values(objectListView, 2)

    # reset the mock from the initial load
    mock_dispatch.reset_mock()
    mock_dispatch.assert_not_any_call(InstanceOf(Action) & Attrs(type=REQUEST_EVENTS))

    refresh_click = next(
        iter(
            [
                a.signals["clicked"]
                for a in widget.actions["analyze"]
                if a.name == "Refresh"
            ]
        )
    )
    refresh_click()
    mock_dispatch.assert_any_call(InstanceOf(Action) & Attrs(type=REQUEST_EVENTS))

    # need to manually execute state reload since we are mocking
    # states array must be rebuild its refs change for the comparison in the
    # PolicyRulesAdminPage.on_next method
    reloaded_states = [
        _build_state(
            events={"log": mock_log()},
            groups={"groups": mock_groups()},
            users={"users": mock_users()},
        )
    ]
    for s in reloaded_states:
        mock_system_features.on_next(s)

    cur_selected_acl = get_selected_values(aclListView, 0)
    assert len(cur_selected_acl) > 0
    assert prev_selected_acl == cur_selected_acl
    cur_selected_subjects = get_selected_values(subjectListView, 2)
    assert len(cur_selected_subjects) > 0
    assert prev_selected_subjects == cur_selected_subjects
    cur_selected_objects = get_selected_values(objectListView, 2)
    assert len(cur_selected_objects) > 0
    assert prev_selected_objects == cur_selected_objects


@pytest.mark.parametrize(
    "aclListView",
    [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")],
)
def test_handles_data_changed_after_refresh(
    aclListView,
    subjectListView,
    objectListView,
    widget,
    mock_system_features,
):
    def get_selected_values(view, data_column_num):
        model, paths = view.get_selection().get_selected_rows()
        return [model.get_value(model.get_iter(p), data_column_num) for p in paths]

    aclListView.get_selection().select_path(Gtk.TreePath.new_first())
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    objectListView.get_selection().select_path(Gtk.TreePath.new_first())

    refresh_click = next(
        iter(
            [
                a.signals["clicked"]
                for a in widget.actions["analyze"]
                if a.name == "Refresh"
            ]
        )
    )
    refresh_click()

    new_events = [
        MagicMock(
            uid=0,
            gid=0,
            subject=MagicMock(file="newFooSubject", trust="ST", access="A"),
            object=MagicMock(file="fooObject", trust="ST", access="A", mode="R"),
        )
    ]
    new_states = [
        _build_state(
            events={
                "log": MagicMock(
                    subjects=lambda: [e.subject.file for e in new_events],
                    by_subject=lambda f: [e for e in new_events if e.subject.file == f],
                    by_user=lambda id: [e for e in new_events if e.uid == id],
                    by_group=lambda id: [e for e in new_events if e.gid == id],
                )
            },
            groups={"groups": mock_groups()},
            users={"users": mock_users()},
        )
    ]

    # need to manually execute state reload since we are mocking
    for s in new_states:
        mock_system_features.on_next(s)

    assert len(get_selected_values(aclListView, 0)) == 1
    assert len(get_selected_values(subjectListView, 2)) == 0
    assert len(get_selected_values(objectListView, 2)) == 0


@pytest.mark.parametrize(
    "aclListView",
    [pytest.lazy_fixture("userListView")],  # , pytest.lazy_fixture("groupListView")],
)
def test_refresh_with_multi_select(
    aclListView, subjectListView, objectListView, widget, mock_system_features
):
    def get_selected_values(view, data_column_num):
        model, paths = view.get_selection().get_selected_rows()
        return [model.get_value(model.get_iter(p), data_column_num) for p in paths]

    aclListView.get_selection().select_path(Gtk.TreePath.new_first())
    subjectListView.get_selection().select_all()
    objectListView.get_selection().select_path(Gtk.TreePath.new_first())

    refresh_click = next(
        iter(
            [
                a.signals["clicked"]
                for a in widget.actions["analyze"]
                if a.name == "Refresh"
            ]
        )
    )
    refresh_click()

    # need to manually execute state reload since we are mocking
    # states array must be rebuild its refs change for the comparison in the
    # PolicyRulesAdminPage.on_next method
    reloaded_states = [
        _build_state(
            events={"log": mock_log()},
            groups={"groups": mock_groups()},
            users={"users": mock_users()},
        )
    ]
    for s in reloaded_states:
        mock_system_features.on_next(s)

    assert len(get_selected_values(aclListView, 0)) == 1
    assert len(get_selected_values(subjectListView, 2)) == 2
    assert len(get_selected_values(objectListView, 2)) == 1


@pytest.mark.parametrize(
    "view, mockFnName",
    [
        (pytest.lazy_fixture("userListView"), "get_user_details"),
        (pytest.lazy_fixture("groupListView"), "get_group_details"),
    ],
)
def test_updates_acl_details(widget, view, mockFnName, mocker):
    mocker.patch(
        f"fapolicy_analyzer.ui.policy_rules_admin_page.acl.{mockFnName}",
        return_value="foo",
    )
    textBuffer = widget.get_object("userDetails").get_buffer()
    view.get_selection().select_path(Gtk.TreePath.new_first())
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_updates_subject_details(widget, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.policy_rules_admin_page.fs.stat", return_value="foo"
    )
    textBuffer = widget.get_object("subjectDetails").get_buffer()
    widget.on_file_selection_changed([MagicMock(file="baz")])
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == "foo"
    )


def test_updates_object_details(widget, mocker):
    mocker.patch(
        "fapolicy_analyzer.ui.policy_rules_admin_page.fs.stat", return_value="foo"
    )
    textBuffer = widget.get_object("objectDetails").get_buffer()
    widget.on_file_selection_changed(
        [MagicMock(file="baz")], type="objects", details_widget_name="objectDetails"
    )
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
    PolicyRulesAdminPage(audit_file=_mock_file)
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


def test_time_not_displayed(mocker, widget):
    time_display = widget.get_object("time_bar")
    assert time_display.get_visible() is False
    assert "time" not in widget.actions.keys()


def test_time_select_button_clicked(mocker):
    page = PolicyRulesAdminPage(use_syslog=True)
    mockDialog = MagicMock()
    mockDialog.run.return_value = 1
    mockDialog.get_seconds.return_value = 3600
    mocker.patch(
        "fapolicy_analyzer.ui.time_select_dialog.TimeSelectDialog.get_ref",
        return_value=mockDialog,
    )

    time_click = next(
        iter(
            [a.signals["clicked"] for a in page.actions["analyze"] if a.name == "Time"]
        )
    )
    time_click()
    mockDialog.run.assert_called()
    assert page._time_delay == 3600


def test_open_file_button_clicked(widget, mock_dispatch, mocker):
    mock_get_Filename = mocker.patch(
        "fapolicy_analyzer.ui.policy_rules_admin_page.FileChooserDialog.get_filename",
        return_value="foo",
    )
    Gtk.Window().add(widget.get_ref())  # add widget to window for dialog parent

    on_click = next(
        iter(
            [
                a.signals["clicked"]
                for a in widget.actions["analyze"]
                if a.name == "Open File"
            ]
        )
    )
    on_click()
    mock_get_Filename.assert_called()
    mock_dispatch.assert_any_call(
        InstanceOf(Action) & Attrs(type=REQUEST_EVENTS, payload=("debug", "foo"))
    )
