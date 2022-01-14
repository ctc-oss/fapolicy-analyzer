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

from functools import partial
from typing import Optional

import gi
from events import Events
from fapolicy_analyzer.util import acl, fs

from .acl_list import ACLList
from .actions import (
    NotificationType,
    add_notification,
    request_events,
    request_groups,
    request_users,
)
from .object_list import ObjectList
from .store import dispatch, get_system_feature
from .strings import (
    GET_GROUPS_LOG_ERROR_MSG,
    GET_USERS_ERROR_MSG,
    GROUP_LABEL,
    GROUPS_LABEL,
    PARSE_EVENT_LOG_ERROR_MSG,
    USER_LABEL,
    USERS_LABEL,
)
from .subject_list import SubjectList
from .ui_page import UIAction, UIPage
from .ui_widget import UIConnectedWidget

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk  # isort: skip


class PolicyRulesAdminPage(UIConnectedWidget, UIPage):
    def __init__(self, audit_file: str = None):
        UIConnectedWidget.__init__(
            self, get_system_feature(), on_next=self.on_next_system
        )

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
        UIPage.__init__(self, actions)

        self.__audit_file: str = audit_file
        self.__log = None
        self.__eventsLoading = False
        self.__users = []
        self.__usersLoading = False
        self.__groups = []
        self.__groupsLoading = False
        self.__systemTrust = []
        self.__ancillaryTrust = []
        self.__selected_user: Optional[int] = None
        self.__selected_group: Optional[int] = None
        self.__selected_subject: Optional[str] = None
        self.__selected_object: Optional[str] = None

        userTabs = self.get_object("userTabs")
        self.userList = ACLList(label=USER_LABEL, label_plural=USERS_LABEL)
        self.groupList = ACLList(label=GROUP_LABEL, label_plural=GROUPS_LABEL)
        userTabs.append_page(self.userList.get_ref(), Gtk.Label(label="User"))
        userTabs.append_page(self.groupList.get_ref(), Gtk.Label(label="Group"))

        userTabs.append_page(
            self.__all_list(),
            Gtk.Label(label="All"),
        )

        subjectTabs = self.get_object("subjectTabs")
        self.subjectList = SubjectList()
        subjectTabs.append_page(self.subjectList.get_ref(), Gtk.Label(label="Subject"))

        objectTabs = self.get_object("objectTabs")
        self.objectList = ObjectList()
        self.objectList.file_selection_changed += self.on_object_selection_changed
        objectTabs.append_page(self.objectList.get_ref(), Gtk.Label(label="Object"))

        self.switchers = [
            self.Switcher(
                self.get_object("userPanel"),
                self.__populate_acls,
                (
                    self.userList,
                    "selection_changed",
                    partial(
                        self.on_user_selection_changed,
                        self.__populate_subjects_from_acl,
                    ),
                    partial(self.on_user_selection_changed, self.__populate_objects),
                ),
                (
                    self.groupList,
                    "selection_changed",
                    partial(
                        self.on_group_selection_changed,
                        self.__populate_subjects_from_acl,
                    ),
                    partial(self.on_group_selection_changed, self.__populate_objects),
                ),
                primary=True,
            ),
            self.Switcher(
                self.get_object("subjectPanel"),
                self.__populate_subjects,
                (
                    self.subjectList,
                    "file_selection_changed",
                    partial(
                        self.on_subject_selection_changed,
                        self.__populate_acls_from_subject,
                    ),
                    partial(self.on_subject_selection_changed, self.__populate_objects),
                ),
            ),
        ]
        for s in self.switchers:
            s.buttonClicked += self.on_switcher_button_clicked

        self.__refresh()

    def __refresh(self):
        self.__usersLoading = True
        dispatch(request_users())
        self.__groupsLoading = True
        dispatch(request_groups())
        self.__eventsLoading = True
        if self.__audit_file:
            dispatch(request_events("debug", self.__audit_file))
        else:
            dispatch(request_events("syslog"))

    def __all_list(self):
        box = Gtk.Box()
        box.set_border_width(10)
        box.add(
            Gtk.Label(label="Show something here that makes sense for the All tab??")
        )
        box.show_all()
        return box

    def __populate_list(
        self,
        list,
        data,
        sensitive,
        selection=None,
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

        # disable changed event handling while loading
        change_events = disable_change_events()

        list.load_store(data, **kwargs)
        list.get_ref().set_sensitive(sensitive)

        # re-enable change event handling
        enable_change_events(change_events)

        # if the selected row still exists in the list, select it again
        if selection and select_func and (row := select_func(selection)):
            list.select_rows(row)
            return selection

        return None

    def __populate_acls(self):

        if self.__usersLoading or self.__groupsLoading or not self.__log:
            return

        users = list(
            {
                e.uid: {"id": u.id, "name": u.name}
                for u in self.__users
                for e in self.__log.by_user(u.id)
            }.values()
        )
        self.__selected_user = self.__populate_list(
            self.userList,
            users,
            True,
            self.__selected_user,
            self.userList.get_selected_row_by_acl_id,
        )

        groups = list(
            {
                e.gid: {"id": g.id, "name": g.name}
                for g in self.__groups
                for e in self.__log.by_group(g.id)
            }.values()
        )
        self.__selected_group = self.__populate_list(
            self.groupList,
            groups,
            True,
            self.__selected_group,
            self.groupList.get_selected_row_by_acl_id,
        )

    def __populate_acls_from_subject(self):
        if not self.__selected_subject:
            self.__selected_user = self.__populate_list(self.userList, [], False)
            self.__selected_group = self.__populate_list(self.groupList, [], False)
            return

        users = list(
            {
                e.uid: {"id": u.id, "name": u.name}
                for e in self.__log.by_subject(self.__selected_subject)
                for u in self.__users
                if e.uid == u.id
            }.values()
        )
        self.__selected_user = self.__populate_list(
            self.userList,
            users,
            True,
            self.__selected_user,
            self.userList.get_selected_row_by_acl_id,
        )

        groups = list(
            {
                e.gid: {"id": g.id, "name": g.name}
                for e in self.__log.by_subject(self.__selected_subject)
                for g in self.__groups
                if e.gid == g.id
            }.values()
        )
        self.__selected_group = self.__populate_list(
            self.groupList,
            groups,
            True,
            self.__selected_group,
            self.groupList.get_selected_row_by_acl_id,
        )

    def __populate_subjects(self):
        if self.__usersLoading or self.__groupsLoading or not self.__log:
            return

        subjects = list(
            {
                e.subject.file: e.subject
                for s in self.__log.subjects()
                for e in self.__log.by_subject(s)
            }.values()
        )
        self.__selected_subject = self.__populate_list(
            self.subjectList,
            subjects,
            True,
            self.__selected_subject,
            self.subjectList.get_selected_row_by_file,
            systemTrust=self.__systemTrust,
            ancillaryTrust=self.__ancillaryTrust,
        )

    def __populate_subjects_from_acl(self):
        if not self.__selected_user and not self.__selected_group:
            self.__selected_subject = self.__populate_list(self.subjectList, [], False)
            return

        subjects = list(
            {
                e.subject.file: e.subject
                for e in (
                    self.__log.by_user(self.__selected_user)
                    if self.__selected_user
                    else self.__log.by_group(self.__selected_group)
                    if self.__selected_group
                    else []
                )
            }.values()
        )
        self.__selected_subject = self.__populate_list(
            self.subjectList,
            subjects,
            True,
            self.__selected_subject,
            self.subjectList.get_selected_row_by_file,
            systemTrust=self.__systemTrust,
            ancillaryTrust=self.__ancillaryTrust,
        )

    def __populate_objects(self):
        if self.__selected_subject and (self.__selected_user or self.__selected_group):
            objects = list(
                {
                    e.object.file: e.object
                    for e in self.__log.by_subject(self.__selected_subject)
                    if e.uid == self.__selected_user or e.gid == self.__selected_group
                }.values()
            )
            self.__selected_object = self.__populate_list(
                self.objectList,
                objects,
                True,
                self.__selected_object,
                self.subjectList.get_selected_row_by_file,
                systemTrust=self.__systemTrust,
                ancillaryTrust=self.__ancillaryTrust,
            )
        else:
            self.__selected_object = self.__populate_list(self.objectList, [], False)

    def __populate_acl_details(self, id, detailsFn):
        userDetails = self.get_object("userDetails")
        details = "\n".join(detailsFn(id).split(" ")) if id else ""
        userDetails.get_buffer().set_text(details)

    def on_next_system(self, system):
        eventsState = system.get("events")
        groupState = system.get("groups")
        userState = system.get("users")

        # these should already be loaded in state from the initial DB Admin Tool load
        self.__systemTrust = system.get("system_trust").trust
        self.__ancillaryTrust = system.get("ancillary_trust").trust

        if eventsState.error and not eventsState.loading and self.__eventsLoading:
            self.__eventsLoading = False
            dispatch(
                add_notification(
                    PARSE_EVENT_LOG_ERROR_MSG,
                    NotificationType.ERROR,
                )
            )
        elif (
            self.__eventsLoading
            and not eventsState.loading
            and self.__log != eventsState.log
        ):
            self.__eventsLoading = False
            self.__log = eventsState.log
            self.__populate_acls()

        if userState.error and not userState.loading and self.__usersLoading:
            self.__usersLoading = False
            dispatch(
                add_notification(
                    GET_USERS_ERROR_MSG,
                    NotificationType.ERROR,
                )
            )
        elif (
            self.__usersLoading
            and not userState.loading
            and self.__users != userState.users
        ):
            self.__usersLoading = False
            self.__users = userState.users
            self.__populate_acls()

        if groupState.error and not groupState.loading and self.__groupsLoading:
            self.__groupsLoading = False
            dispatch(
                add_notification(
                    GET_GROUPS_LOG_ERROR_MSG,
                    NotificationType.ERROR,
                )
            )
        elif (
            self.__groupsLoading
            and not groupState.loading
            and self.__groups != groupState.groups
        ):
            self.__groupsLoading = False
            self.__groups = groupState.groups
            self.__populate_acls()

        self.userList.set_loading(
            self.__eventsLoading or self.__usersLoading or self.__groupsLoading
        )
        self.groupList.set_loading(
            self.__eventsLoading or self.__usersLoading or self.__groupsLoading
        )

    def on_user_selection_changed(self, secondaryAction, data):
        uid = data[-1][1] if data else None
        if uid != self.__selected_user:
            self.__selected_user = uid
            self.__selected_group = None
            self.__populate_acl_details(uid, acl.getUserDetails)
            secondaryAction()

    def on_group_selection_changed(self, secondaryAction, data):
        gid = data[-1][1] if data else None
        if gid != self.__selected_group:
            self.__selected_group = gid
            self.__selected_user = None
            self.__populate_acl_details(gid, acl.getGroupDetails)
            secondaryAction()

    def on_subject_selection_changed(self, secondaryAction, data):
        subject = data[-1].file if data else None
        if subject == self.__selected_subject:
            return

        self.__selected_subject = subject
        subjectDetails = self.get_object("subjectDetails")
        subjectDetails.get_buffer().set_text(fs.stat(subject) if subject else "")
        secondaryAction()

    def on_object_selection_changed(self, data):
        object = data[-1].file if data else None
        self.__selected_object = object
        objectDetails = self.get_object("objectDetails")
        objectDetails.get_buffer().set_text(fs.stat(object) if object else "")

    def on_switcher_button_clicked(self, switcher):
        switcher.set_as_secondary()
        rest = [x for x in self.switchers if x != switcher]
        for s in rest:
            s.set_as_primary()

    def on_userTabs_switch_page(self, notebook, page, page_num):
        if page_num != 0:
            self.userList.treeView.get_selection().unselect_all()
        if page_num != 1:
            self.groupList.treeView.get_selection().unselect_all()

    def on_refresh_clicked(self, *args):
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

        def set_as_primary(self):
            self.__panel.get_parent().reorder_child(self.__panel, 0)
            for x in self.__lists:
                lst = x["list"]
                lst.set_action_buttons(*lst.get_action_buttons(), x["button"])
                lst.get_ref().set_sensitive(True)
                self.__switch_change_handlers(lst, x["event"], x["primaryHandler"])

            self.__dataFunc()

        def set_as_secondary(self):
            for x in self.__lists:
                lst = x["list"]
                lst.set_action_buttons(
                    *[b for b in lst.get_action_buttons() if b != x["button"]]
                )
                lst.get_ref().set_sensitive(False)
                lst.load_store([])
                self.__switch_change_handlers(lst, x["event"], x["secondaryHandler"])
