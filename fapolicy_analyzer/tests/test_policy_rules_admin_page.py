import context  # noqa: F401
import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from unittest.mock import MagicMock
from helpers import refresh_gui
from ui.policy_rules_admin_page import PolicyRulesAdminPage


def mock_users():
    mockUser1 = MagicMock(id=1)
    mockUser1.name = "fooUser"
    mockUser2 = MagicMock(id=2)
    mockUser2.name = "otherUser"
    return [mockUser1, mockUser2]


def mock_groups():
    mockGroup1 = MagicMock(id=100)
    mockGroup1.name = "fooGroup"
    mockGroup2 = MagicMock(id=101)
    mockGroup2.name = "otherGroup"
    return [mockGroup1, mockGroup2]


mock_events = [
    MagicMock(
        uid=1,
        gid=100,
        subject=MagicMock(file="fooSubject", trust="ST", access="A"),
        object=MagicMock(file="fooObject", trust="ST", access="A", mode="R"),
    ),
    MagicMock(
        uid=2,
        gid=101,
        subject=MagicMock(file="otherSubject", trust="ST", access="A"),
        object=MagicMock(file="otherObject", trust="ST", access="A", mode="R"),
    ),
]


@pytest.fixture
def widget(mocker):
    mock_system = MagicMock(
        users=MagicMock(return_value=mock_users()),
        groups=MagicMock(return_value=mock_groups()),
        events_from=MagicMock(return_value=mock_events),
    )

    mocker.patch(
        "ui.ancillary_trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    mocker.patch(
        "ui.trust_file_list.epoch_to_string",
        return_value="10-01-2020",
    )

    mocker.patch("ui.policy_rules_admin_page.System", return_value=mock_system)
    widget = PolicyRulesAdminPage("foo")
    refresh_gui()
    return widget


@pytest.fixture
def userListView(widget):
    return widget.userList.get_object("treeView")


@pytest.fixture
def groupListView(widget):
    return widget.groupList.get_object("treeView")


@pytest.fixture
def subjectListView(widget):
    return widget.subjectList.get_object("treeView")


@pytest.fixture
def objectListView(widget):
    return widget.objectList.get_object("treeView")


@pytest.fixture
def activeSwitcherButton(widget):
    # find switcher button, either the 1st button in the user list
    # or 2nd button in subject list. Only 1 should exist at any point in time.
    return next(
        iter(
            [
                *widget.userList.get_action_buttons()[0:],
                *widget.subjectList.get_action_buttons()[1:],
            ]
        )
    )


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


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


def test_loads_users_primary(widget, userListView):
    model = userListView.get_model()
    assert len(model) == 2
    assert [x.name for x in mock_users()] == [x[0] for x in model]
    assert [x.id for x in mock_users()] == [x[1] for x in model]


def test_loads_groups_primary(widget, groupListView):
    model = groupListView.get_model()
    assert len(model) == 2
    assert [x.name for x in mock_groups()] == [x[0] for x in model]
    assert [x.id for x in mock_groups()] == [x[1] for x in model]


def test_loads_subjects_primary(widget, subjectListView, activeSwitcherButton):
    activeSwitcherButton.clicked()
    model = subjectListView.get_model()
    expectedSubjects = [e.subject for e in mock_events]
    assert len(model) == 2
    for idx, expectedSubject in enumerate(expectedSubjects):
        assert expectedSubject.trust in model[idx][0]
        assert expectedSubject.access in model[idx][1]
        assert expectedSubject.file == model[idx][2]


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_loads_subjects_secondary(widget, view, subjectListView):
    view.get_selection().select_path(Gtk.TreePath.new_first())
    model = subjectListView.get_model()
    expectedSubject = mock_events[0].subject
    assert len(model) == 1
    assert expectedSubject.trust in next(iter([x[0] for x in model]))
    assert expectedSubject.access in next(iter([x[1] for x in model]))
    assert expectedSubject.file == next(iter([x[2] for x in model]))


def test_loads_users_secondary(
    widget, userListView, activeSwitcherButton, subjectListView
):
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
    widget, groupListView, activeSwitcherButton, subjectListView
):
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
def test_loads_objects_from_subject(widget, view, subjectListView, objectListView):
    view.get_selection().select_path(Gtk.TreePath.new_first())
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    model = objectListView.get_model()
    expectedObject = mock_events[0].object
    assert expectedObject.trust in next(iter([x[0] for x in model]))
    assert expectedObject.mode in next(iter([x[1] for x in model]))
    assert expectedObject.access in next(iter([x[2] for x in model]))
    assert expectedObject.file == next(iter([x[3] for x in model]))


@pytest.mark.parametrize(
    "view", [pytest.lazy_fixture("userListView"), pytest.lazy_fixture("groupListView")]
)
def test_loads_objects_from_acl(
    widget, view, subjectListView, objectListView, activeSwitcherButton
):
    activeSwitcherButton.clicked()
    subjectListView.get_selection().select_path(Gtk.TreePath.new_first())
    view.get_selection().select_path(Gtk.TreePath.new_first())
    model = objectListView.get_model()
    expectedObject = mock_events[0].object
    assert expectedObject.trust in next(iter([x[0] for x in model]))
    assert expectedObject.mode in next(iter([x[1] for x in model]))
    assert expectedObject.access in next(iter([x[2] for x in model]))
    assert expectedObject.file == next(iter([x[3] for x in model]))


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
    widget.on_object_selection_changed(MagicMock(file=""))
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
    assert widget.subjectList.get_ref().get_sensitive()
    assert len([x for x in subjectListView.get_model()]) > 0
    view.get_selection().unselect_all()
    textBuffer = widget.get_object("userDetails").get_buffer()
    assert (
        textBuffer.get_text(
            textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
        )
        == ""
    )
    assert not widget.subjectList.get_ref().get_sensitive()
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
    assert widget.objectList.get_ref().get_sensitive()
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
    assert not widget.objectList.get_ref().get_sensitive()
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
