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

from functools import partial
from os import path
from typing import Optional, Sequence

import gi
from events import Events

from fapolicy_analyzer import EventLog, Group, Trust, User
from fapolicy_analyzer.ui.acl_list import ACLList
from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    request_events,
    request_groups,
    request_users,
)
from fapolicy_analyzer.ui.file_chooser_dialog import FileChooserDialog
from fapolicy_analyzer.ui.object_list import ObjectList
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.ui.strings import (
    GET_GROUPS_LOG_ERROR_MSG,
    GET_USERS_ERROR_MSG,
    GROUP_LABEL,
    GROUPS_LABEL,
    OPEN_FILE_LABEL,
    PARSE_EVENT_LOG_ERROR_MSG,
    SYSLOG_FORMAT_WARNING,
    TIME_FORMAT_CONFIG_TITLE,
    USER_LABEL,
    USERS_LABEL,
)
from fapolicy_analyzer.ui.subject_list import SubjectList
from fapolicy_analyzer.ui.time_select_dialog import TimeSelectDialog
from fapolicy_analyzer.ui.ui_page import UIAction, UIPage
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget
from fapolicy_analyzer.util import acl, fs

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip
import time


def time_format_config_dlg():

    dlgTimeFormatConfig = Gtk.Dialog(
        title=TIME_FORMAT_CONFIG_TITLE
    )
    dlgTimeFormatConfig.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)

    label = Gtk.Label(label=SYSLOG_FORMAT_WARNING)
    hbox = dlgTimeFormatConfig.get_content_area()
    label.set_justify(Gtk.Justification.LEFT)
    hbox.add(label)
    dlgTimeFormatConfig.show_all()
    dlgTimeFormatConfig.run()
    dlgTimeFormatConfig.destroy()


class PolicyRulesAdminPage(UIConnectedWidget, UIPage):
    def __init__(self, use_syslog: bool = False, audit_file: Optional[str] = None):
        UIConnectedWidget.__init__(
            self, get_system_feature(), on_next=self.on_next_system
        )

        self.__use_syslog = use_syslog
        self.__audit_file = audit_file

        actions = {
            "analyze": [
                UIAction(
                    "Refresh",
                    "Refresh Data",
                    "view-refresh",
                    {"clicked": self.on_refresh_clicked},
                )
            ]
        }
        if use_syslog:
            actions["analyze"] = [
                *actions["analyze"],
                UIAction(
                    "Time",
                    "Time Selection",
                    "alarm-symbolic",
                    {"clicked": self.on_timeSelectBtn_clicked},
                ),
            ]
        else:
            actions["analyze"] = [
                *actions["analyze"],
                UIAction(
                    "Open File",
                    "Open Log File",
                    "document-open",
                    {"clicked": self.on_openFileBtn_clicked},
                ),
            ]

        UIPage.__init__(self, actions)
        self.__n_changesets = 0

        self.__log: Optional[Sequence[EventLog]] = None
        self.__events_loading = False
        self.__users: Sequence[User] = []
        self.__users_loading = False
        self.__groups: Sequence[Group] = []
        self.__groups_loading = False
        self.__system_trust: Sequence[Trust] = []
        self.__ancillary_trust: Sequence[Trust] = []
        self.__selection_state = {
            "user": None,
            "group": None,
            "subjects": None,
            "objects": None,
        }

        user_tabs = self.get_object("userTabs")
        self.user_list = ACLList(label=USER_LABEL, label_plural=USERS_LABEL)
        self.group_list = ACLList(label=GROUP_LABEL, label_plural=GROUPS_LABEL)
        user_tabs.append_page(self.user_list.get_ref(), Gtk.Label(label="User"))
        user_tabs.append_page(self.group_list.get_ref(), Gtk.Label(label="Group"))

        subject_tabs = self.get_object("subjectTabs")
        self.subject_list = SubjectList()
        subject_tabs.append_page(
            self.subject_list.get_ref(), Gtk.Label(label="Subject")
        )

        object_tabs = self.get_object("objectTabs")
        self.object_list = ObjectList()
        self.object_list.file_selection_changed += partial(
            self.on_file_selection_changed,
            type="objects",
            details_widget_name="objectDetails",
        )
        object_tabs.append_page(self.object_list.get_ref(), Gtk.Label(label="Object"))

        self.get_object("delayDisplay").set_text("1 Hour")
        self._time_delay = -1
        self.__time_unit = "2"
        self.__time_number = 1
        self.when_none = 0
        self.__switchers = [
            self.Switcher(
                self.get_object("userPanel"),
                self.__populate_acls,
                (
                    self.user_list,
                    "selection_changed",
                    partial(
                        self.on_acl_selection_changed,
                        type="user",
                        secondary_action=self.__populate_subjects_from_acl,
                    ),
                    partial(
                        self.on_acl_selection_changed,
                        type="user",
                        secondary_action=self.__populate_objects,
                    ),
                ),
                (
                    self.group_list,
                    "selection_changed",
                    partial(
                        self.on_acl_selection_changed,
                        type="group",
                        secondary_action=self.__populate_subjects_from_acl,
                    ),
                    partial(
                        self.on_acl_selection_changed,
                        type="group",
                        secondary_action=self.__populate_objects,
                    ),
                ),
                primary=True,
            ),
            self.Switcher(
                self.get_object("subjectPanel"),
                self.__populate_subjects,
                (
                    self.subject_list,
                    "file_selection_changed",
                    partial(
                        self.on_file_selection_changed,
                        secondary_action=self.__populate_acls_from_subject,
                    ),
                    partial(
                        self.on_file_selection_changed,
                        secondary_action=self.__populate_objects,
                    ),
                ),
            ),
        ]
        for s in self.__switchers:
            s.buttonClicked += self.on_switcher_button_clicked

        self.__refresh()

    def __refresh(self):
        self.__users_loading = True
        self.__groups_loading = True
        dispatch(request_users())
        dispatch(request_groups())
        if self.__use_syslog:
            self.__events_loading = True
            dispatch(request_events("syslog"))
            self.get_object("time_bar").set_visible(True)
        elif self.__audit_file:
            self.__events_loading = True
            dispatch(request_events("debug", self.__audit_file))

    def __populate_list(
        self,
        list,
        data,
        type,
        sensitive=False,
        select_func=None,
        **kwargs,
    ):
        """
        Populates the list with the data then selects the rows. The rows will be
        selected only if the give selection data can be found in the row using the
        select_func. If found the row is selected and returned if not found None is
        returned.
        """

        def disable_change_events():
            change_events = []
            for e in list.selection_changed:
                change_events.append(e)
                list.selection_changed -= e
            return change_events

        def enable_change_events(change_events):
            for e in change_events:
                list.selection_changed += e

        def reselect_rows():
            selections = self.__selection_state[type]
            rows = []
            if selections is not None and select_func:
                selections = (
                    selections if isinstance(selections, Sequence) else [selections]
                )
                for s in selections:
                    row = select_func(s)
                    if row:
                        rows += [row]
                self.__selection_state[type] = None

            if not rows:
                return False

            # if more than one row to select disable events except for the last row
            if len(rows) > 1:
                original_events = disable_change_events()
                rows_minus_1 = len(rows) - 1
                list.select_rows(*rows[0:rows_minus_1])
                enable_change_events(original_events)

            list.select_rows(rows[-1])
            return True

        # disable changed event handling while loading
        original_events = disable_change_events()

        list.load_store(data, **kwargs)
        list.get_ref().set_sensitive(sensitive)

        # re-enable change event handling
        enable_change_events(original_events)

        if not reselect_rows():
            list.selection_changed(None)

    def __is_any_data_loading(self):
        return self.__users_loading or self.__groups_loading or self.__events_loading

    def __populate_acls(self, users=None, groups=None):

        if self.__is_any_data_loading() or not self.__log:
            return

        users = users or list(
            {
                e.uid: {"id": u.id, "name": u.name}
                for u in self.__users
                for e in self.__log.by_user(u.id)
            }.values()
        )
        self.__populate_list(
            self.user_list,
            users,
            "user",
            True,
            self.user_list.get_selected_row_by_acl_id,
        )

        groups = groups or list(
            {
                e.gid: {"id": g.id, "name": g.name}
                for g in self.__groups
                for e in self.__log.by_group(g.id)
            }.values()
        )
        self.__populate_list(
            self.group_list,
            groups,
            "group",
            True,
            self.group_list.get_selected_row_by_acl_id,
        )

    def __populate_acls_from_subject(self):
        if not self.__selection_state["subjects"]:
            self.__populate_list(self.user_list, [], "user")
            self.__populate_list(self.group_list, [], "group")
            return

        last_selection = self.__selection_state["subjects"][-1]
        users = list(
            {
                e.uid: {"id": u.id, "name": u.name}
                for e in self.__log.by_subject(last_selection)
                for u in self.__users
                if e.uid == u.id
            }.values()
        )
        groups = list(
            {
                e.gid: {"id": g.id, "name": g.name}
                for e in self.__log.by_subject(last_selection)
                for g in self.__groups
                if e.gid == g.id
            }.values()
        )

        self.__populate_acls(users=users, groups=groups)

    def __populate_subjects(self, subjects=None):
        if self.__users_loading or self.__groups_loading or not self.__log:
            return

        subjects = subjects or list(
            {
                e.subject.file: e.subject
                for s in self.__log.subjects()
                for e in self.__log.by_subject(s)
            }.values()
        )
        self.__populate_list(
            self.subject_list,
            subjects,
            "subjects",
            True,
            self.subject_list.get_selected_row_by_file,
            systemTrust=self.__system_trust,
            ancillaryTrust=self.__ancillary_trust,
        )

    def __populate_subjects_from_acl(self):
        if (
            self.__selection_state["user"] is None
            and self.__selection_state["group"] is None
        ):
            self.__populate_list(self.subject_list, [], "subjects")
            return

        subjects = list(
            {
                e.subject.file: e.subject
                for e in (
                    self.__log.by_user(self.__selection_state["user"])
                    if self.__selection_state["user"] is not None
                    else self.__log.by_group(self.__selection_state["group"])
                    if self.__selection_state["group"] is not None
                    else []
                )
            }.values()
        )
        self.__populate_subjects(subjects=subjects)

    def __populate_objects(self):
        if self.__selection_state["subjects"] and (
            self.__selection_state["user"] is not None
            or self.__selection_state["group"] is not None
        ):
            last_subject = self.__selection_state["subjects"][-1]
            self.when_none = sum([True for e in self.__log.by_subject(last_subject) if e.when() is None])
            data = list(
                {
                    e.object.file: {e.rule_id: e.object}
                    for e in self.__log.by_subject(last_subject)
                    if e.uid == self.__selection_state["user"]
                    or e.gid == self.__selection_state["group"]
                }.values()
            )

            self.__populate_list(
                self.object_list,
                data,
                "objects",
                True,
                self.object_list.get_selected_row_by_file,
                systemTrust=self.__system_trust,
                ancillaryTrust=self.__ancillary_trust,
            )
        else:
            self.__populate_list(self.object_list, [], "objects")

    def __get_audit_file(self) -> Optional[str]:
        fcd = FileChooserDialog(
            title=OPEN_FILE_LABEL,
            parent=self.get_ref().get_toplevel(),
        )

        _file = fcd.get_filename() or ""
        if path.isfile(_file):
            return _file

        fcd.destroy()

    def on_next_system(self, system):
        def exec_primary_data_func():
            next(
                iter([s for s in self.__switchers if s.get_is_primary()])
            ).exec_data_func()

        eventsState = system.get("events")
        groupState = system.get("groups")
        userState = system.get("users")

        # these should already be loaded in state from the initial DB Admin Tool load
        self.__system_trust = system.get("system_trust").trust
        self.__ancillary_trust = system.get("ancillary_trust").trust

        if eventsState.error and not eventsState.loading and self.__events_loading:
            self.__events_loading = False
            dispatch(
                add_notification(
                    PARSE_EVENT_LOG_ERROR_MSG,
                    NotificationType.ERROR,
                )
            )
        elif (
            self.__events_loading
            and not eventsState.loading
            and self.__log != eventsState.log
        ):
            self.__events_loading = False
            self.__log = eventsState.log
            tzdelta = int(time.localtime().tm_gmtoff)
            if self._time_delay < 0:
                self.__log.begin(int(time.time()) + tzdelta - 3600)
            else:
                self.__log.begin(int(time.time()) + tzdelta - self._time_delay)
            exec_primary_data_func()

        if userState.error and not userState.loading and self.__users_loading:
            self.__users_loading = False
            dispatch(
                add_notification(
                    GET_USERS_ERROR_MSG,
                    NotificationType.ERROR,
                )
            )
        elif (
            self.__users_loading
            and not userState.loading
            and self.__users != userState.users
        ):
            self.__users_loading = False
            self.__users = userState.users
            exec_primary_data_func()

        if groupState.error and not groupState.loading and self.__groups_loading:
            self.__groups_loading = False
            dispatch(
                add_notification(
                    GET_GROUPS_LOG_ERROR_MSG,
                    NotificationType.ERROR,
                )
            )
        elif (
            self.__groups_loading
            and not groupState.loading
            and self.__groups != groupState.groups
        ):
            self.__groups_loading = False
            self.__groups = groupState.groups
            exec_primary_data_func()

        self.user_list.set_loading(
            self.__events_loading or self.__users_loading or self.__groups_loading
        )
        self.group_list.set_loading(
            self.__events_loading or self.__users_loading or self.__groups_loading
        )

        num_changesets = len(system.get("changesets", []))
        if self.__n_changesets != num_changesets:
            self.__n_changesets = num_changesets
            self.__refresh()

    def on_acl_selection_changed(self, data, type=None, secondary_action=None):
        id = data[-1][1] if data else None
        if id != self.__selection_state[type]:
            self.__selection_state[type] = id
            self.__selection_state["group" if type == "user" else "user"] = None
            details_func = getattr(acl, f"get_{type}_details", None)

            userDetails = self.get_object("userDetails")
            details = (
                "\n".join((details_func(id) or "").split(" ")) if details_func else ""
            )
            userDetails.get_buffer().set_text(details)

            if secondary_action:
                secondary_action()

    def on_file_selection_changed(
        self,
        data,
        type="subjects",
        details_widget_name="subjectDetails",
        secondary_action=None,
    ):
        files = [d.file for d in data or []]
        if files == self.__selection_state[type]:
            return

        self.__selection_state[type] = files
        last_selection = next(iter(files[-1:]), None)
        details = self.get_object(details_widget_name)
        details.get_buffer().set_text(fs.stat(last_selection) if last_selection else "")

        if secondary_action:
            secondary_action()

    def on_switcher_button_clicked(self, switcher):
        switcher.set_as_secondary()
        rest = [x for x in self.__switchers if x != switcher]
        for s in rest:
            s.set_as_primary()
        self.__selection_state = dict.fromkeys(self.__selection_state, None)
        self.__populate_objects()

    def on_userTabs_switch_page(self, notebook, page, page_num):
        if page_num != 0:
            self.user_list.unselect_all_rows()
        if page_num != 1:
            self.group_list.unselect_all_rows()

    def on_refresh_clicked(self, *args):
        self.__refresh()

    def on_timeSelectBtn_clicked(self, *args):
        def plural(count):
            return "s" if count > 1 else ""

        if self.when_none:
            time_format_config_dlg()

        time_dialog = TimeSelectDialog()
        time_dialog.set_time_unit(self.__time_unit)
        time_dialog.set_time_number(self.__time_number)
        resp = time_dialog.get_ref().run()
        time_dialog.get_ref().hide()
        if resp > 0:
            self._time_delay = time_dialog.get_seconds()
            self.__time_unit = time_dialog.get_time_unit()
            self.__time_number = time_dialog.get_time_number()
            disp_string = f"{self.__time_number} {time_dialog.get_unit_str()}{plural(self.__time_number)}"
            self.get_object("delayDisplay").set_text(disp_string)

            self.__refresh()
            self.__populate_acls()
            self.__populate_subjects_from_acl()

    def on_openFileBtn_clicked(self, *args):
        self.__audit_file = self.__get_audit_file()
        if self.__audit_file:
            self.__refresh()

    class Switcher(Events):
        __events__ = ["buttonClicked"]

        def __init__(self, panel, dataFunc, *lists, primary=False):
            Events.__init__(self)
            self.__panel = panel
            self.__dataFunc = dataFunc
            self.__lists = [
                {
                    "list": x[0],
                    "button": self.__button(),
                    "event": x[1],
                    "primaryHandler": x[2],
                    "secondaryHandler": x[3],
                }
                for x in lists
            ]
            if primary:
                self.set_as_primary()
            else:
                self.set_as_secondary()

        def __button(self):
            button = Gtk.Button.new_from_icon_name(
                "network-transmit-receive-symbolic", Gtk.IconSize.BUTTON
            )
            button.connect("clicked", self.__on_button_clicked)
            return button

        def __on_button_clicked(self, *args):
            self.buttonClicked(self)

        def __switch_change_handlers(self, lst, event, handler):
            handlers = getattr(lst, event)

            # remove all handlers
            for h in handlers:
                handlers.__isub__(h)

            # add new handler
            handlers.__iadd__(handler)

        def exec_data_func(self):
            self.__dataFunc()

        def get_is_primary(self):
            return self.__primary

        def set_as_primary(self):
            self.__primary = True
            self.__panel.get_parent().reorder_child(self.__panel, 0)
            for x in self.__lists:
                lst = x["list"]
                lst.set_action_buttons(*lst.get_action_buttons(), x["button"])
                lst.get_ref().set_sensitive(True)
                self.__switch_change_handlers(lst, x["event"], x["primaryHandler"])

            self.exec_data_func()

        def set_as_secondary(self):
            self.__primary = False
            for x in self.__lists:
                lst = x["list"]
                lst.set_action_buttons(
                    *[b for b in lst.get_action_buttons() if b != x["button"]]
                )
                lst.get_ref().set_sensitive(False)
                lst.load_store([])
                self.__switch_change_handlers(lst, x["event"], x["secondaryHandler"])
