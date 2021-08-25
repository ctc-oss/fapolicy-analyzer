import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from concurrent.futures import ThreadPoolExecutor
from events import Events
from fapolicy_analyzer import System
from functools import partial
from .object_list import ObjectList
from .acl_list import ACLList
from .strings import GROUP_LABEL, GROUPS_LABEL, USER_LABEL, USERS_LABEL
from .subject_list import SubjectList
from .ui_widget import UIWidget
from fapolicy_analyzer.util import acl, fs


class PolicyRulesAdminPage(UIWidget):
    def __init__(self, auditFile=None):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.events = []
        self.users = []
        self.groups = []
        self.selectedUser = None
        self.selectedGroup = None
        self.selectedSubject = None

        userTabs = self.get_object("userTabs")
        self.userList = ACLList(label=USER_LABEL, label_plural=USERS_LABEL)
        userTabs.append_page(self.userList.get_ref(), Gtk.Label(label="User"))

        self.groupList = ACLList(label=GROUP_LABEL, label_plural=GROUPS_LABEL)
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
        self.objectList.object_selection_changed += self.on_object_selection_changed
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
                        self.__populate_subjects_acl,
                    ),
                    partial(self.on_user_selection_changed, self.__populate_objects),
                ),
                (
                    self.groupList,
                    "selection_changed",
                    partial(
                        self.on_group_selection_changed,
                        self.__populate_subjects_acl,
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
                    "subject_selection_changed",
                    partial(
                        self.on_subject_selection_changed,
                        self.__populate_acls,
                    ),
                    partial(self.on_subject_selection_changed, self.__populate_objects),
                ),
            ),
        ]
        for s in self.switchers:
            s.buttonClicked += self.on_switcher_button_clicked

        if auditFile:
            self.__load_data(auditFile)

    def __load_data(self, auditFile):
        def process():
            system = System()
            self.events = system.events_from(auditFile)
            self.users = system.users()
            self.groups = system.groups()
            GLib.idle_add(self.__populate_acls)

        self.userList.set_loading(True)
        self.groupList.set_loading(True)
        self.subjectList.get_ref().set_sensitive(False)
        self.objectList.get_ref().set_sensitive(False)
        self.executor.submit(process)

    def __all_list(self):
        box = Gtk.Box()
        box.set_border_width(10)
        box.add(
            Gtk.Label(label="Show something here that makes sense for the All tab??")
        )
        box.show_all()
        return box

    def __populate_acls(self, *args):
        users = list(
            {
                e.uid: {"id": u.id, "name": u.name}
                for u in self.users
                for e in self.events
                if e.uid == u.id
                and (not self.selectedSubject or e.subject.file == self.selectedSubject)
            }.values()
        )
        groups = list(
            {
                e.gid: {"id": g.id, "name": g.name}
                for g in self.groups
                for e in self.events
                if e.gid == g.id
                and (not self.selectedSubject or e.subject.file == self.selectedSubject)
            }.values()
        )
        self.userList.load_store(users)
        self.userList.get_ref().set_sensitive(True)
        self.groupList.load_store(groups)
        self.groupList.get_ref().set_sensitive(True)

    def __populate_acl_details(self, id, detailsFn):
        userDetails = self.get_object("userDetails")
        details = "\n".join(detailsFn(id).split(" ")) if id else ""
        userDetails.get_buffer().set_text(details)

    def __populate_subjects(self, secondary=False):
        if secondary and not self.selectedUser and not self.selectedGroup:
            self.subjectList.get_ref().set_sensitive(False)
            self.subjectList.load_store([])
            return

        subjects = list(
            {
                e.subject.file: e.subject
                for e in self.events
                if (not self.selectedUser or e.uid == self.selectedUser)
                and (not self.selectedGroup or e.gid == self.selectedGroup)
            }.values()
        )
        self.subjectList.load_store(subjects)
        self.subjectList.get_ref().set_sensitive(True)

    def __populate_subjects_acl(self):
        self.__populate_subjects(True)

    def __populate_objects(self):
        if self.selectedSubject and (self.selectedUser or self.selectedGroup):
            self.objectList.get_ref().set_sensitive(True)
            objects = list(
                {
                    e.object.file: e.object
                    for e in self.events
                    if e.subject.file == self.selectedSubject
                    and (e.uid == self.selectedUser or e.gid == self.selectedGroup)
                }.values()
            )
        else:
            self.objectList.get_ref().set_sensitive(False)
            objects = []

        self.objectList.load_store(objects)

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
