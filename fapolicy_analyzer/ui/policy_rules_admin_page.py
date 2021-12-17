# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
import gi

gi.require_version("Gtk", "3.0")
from functools import partial

from events import Events
from fapolicy_analyzer.util import acl, fs
from gi.repository import Gtk

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
from .ui_widget import UIConnectedWidget


class PolicyRulesAdminPage(UIConnectedWidget):
    def __init__(self, auditFile=None):
        super().__init__(get_system_feature(), on_next=self.on_next_system)
        self.__log = None
        self.__eventsLoading = False
        self.__users = []
        self.__usersLoading = False
        self.__groups = []
        self.__groupsLoading = False
        self.__systemTrust = []
        self.__ancillaryTrust = []
        self.selectedUser = None
        self.selectedGroup = None
        self.selectedSubject = None

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

        if auditFile:
            self.__usersLoading = True
            dispatch(request_users())
            self.__groupsLoading = True
            dispatch(request_groups())
            self.__eventsLoading = True
            dispatch(request_events(auditFile))

    def __all_list(self):
        box = Gtk.Box()
        box.set_border_width(10)
        box.add(
            Gtk.Label(label="Show something here that makes sense for the All tab??")
        )
        box.show_all()
        return box

    def __populate_list(self, list, data, sensitive, **kwargs):
        list.load_store(data, **kwargs)
        list.get_ref().set_sensitive(sensitive)

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
        groups = list(
            {
                e.gid: {"id": g.id, "name": g.name}
                for g in self.__groups
                for e in self.__log.by_group(g.id)
            }.values()
        )
        self.__populate_list(self.userList, users, True)
        self.__populate_list(self.groupList, groups, True)

    def __populate_acls_from_subject(self):
        if not self.selectedSubject:
            self.__populate_list(self.userList, [], False)
            self.__populate_list(self.groupList, [], False)
            return

        users = list(
            {
                e.uid: {"id": u.id, "name": u.name}
                for e in self.__log.by_subject(self.selectedSubject)
                for u in self.__users
                if e.uid == u.id
            }.values()
        )
        groups = list(
            {
                e.gid: {"id": g.id, "name": g.name}
                for e in self.__log.by_subject(self.selectedSubject)
                for g in self.__groups
                if e.gid == g.id
            }.values()
        )
        self.__populate_list(self.userList, users, True)
        self.__populate_list(self.groupList, groups, True)

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
        self.__populate_list(
            self.subjectList,
            subjects,
            True,
            systemTrust=self.__systemTrust,
            ancillaryTrust=self.__ancillaryTrust,
        )

    def __populate_subjects_from_acl(self):
        if not self.selectedUser and not self.selectedGroup:
            self.__populate_list(self.subjectList, [], False)
            return

        subjects = list(
            {
                e.subject.file: e.subject
                for e in (
                    self.__log.by_user(self.selectedUser)
                    if self.selectedUser
                    else self.__log.by_group(self.selectedGroup)
                    if self.selectedGroup
                    else []
                )
            }.values()
        )
        self.__populate_list(
            self.subjectList,
            subjects,
            True,
            systemTrust=self.__systemTrust,
            ancillaryTrust=self.__ancillaryTrust,
        )

    def __populate_objects(self):
        if self.selectedSubject and (self.selectedUser or self.selectedGroup):
            objects = list(
                {
                    e.object.file: e.object
                    for e in self.__log.by_subject(self.selectedSubject)
                    if e.uid == self.selectedUser or e.gid == self.selectedGroup
                }.values()
            )
            self.__populate_list(
                self.objectList,
                objects,
                True,
                systemTrust=self.__systemTrust,
                ancillaryTrust=self.__ancillaryTrust,
            )
        else:
            self.__populate_list(self.objectList, [], False)

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
        uid = data[1] if data else None
        if uid != self.selectedUser:
            self.selectedUser = uid
            self.selectedGroup = None
            self.__populate_acl_details(uid, acl.getUserDetails)
            secondaryAction()

    def on_group_selection_changed(self, secondaryAction, data):
        gid = data[1] if data else None
        if gid != self.selectedGroup:
            self.selectedGroup = gid
            self.selectedUser = None
            self.__populate_acl_details(gid, acl.getGroupDetails)
            secondaryAction()

    def on_subject_selection_changed(self, secondaryAction, data):
        subject = data.file if data else None
        if subject == self.selectedSubject:
            return

        self.selectedSubject = subject
        subjectDetails = self.get_object("subjectDetails")
        subjectDetails.get_buffer().set_text(fs.stat(subject) if subject else "")
        secondaryAction()

    def on_object_selection_changed(self, data):
        objectDetails = self.get_object("objectDetails")
        objectDetails.get_buffer().set_text(fs.stat(data.file) if data else "")

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
