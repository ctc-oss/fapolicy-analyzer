import gi

# import fapolicy_analyzer.ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from concurrent.futures import ThreadPoolExecutor
from fapolicy_analyzer import System
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

        userTabs = self.get_object("userTabs")
        self.userList = ACLList(label=USER_LABEL, label_plural=USERS_LABEL)
        self.userList.selection_changed = self.on_user_selection_changed
        userTabs.append_page(self.userList.get_ref(), Gtk.Label(label="User"))

        self.groupList = ACLList(label=GROUP_LABEL, label_plural=GROUPS_LABEL)
        self.groupList.selection_changed = self.on_group_selection_changed
        userTabs.append_page(self.groupList.get_ref(), Gtk.Label(label="Group"))

        userTabs.append_page(
            self.__all_list(),
            Gtk.Label(label="All"),
        )

        subjectTabs = self.get_object("subjectTabs")
        self.subjectList = SubjectList()
        self.subjectList.subject_selection_changed += self.on_subject_selection_changed
        subjectTabs.append_page(self.subjectList.get_ref(), Gtk.Label(label="Subject"))

        objectTabs = self.get_object("objectTabs")
        self.objectList = ObjectList()
        self.objectList.object_selection_changed += self.on_object_selection_changed
        objectTabs.append_page(self.objectList.get_ref(), Gtk.Label(label="Object"))

        if auditFile:
            print("loading events")
            self.__load_events(auditFile)

    def __load_events(self, auditFile):
        def process():
            try:
                system = System()
                print("using system ", system)
                self.events = system.events_from(auditFile)

                users = list(
                    {
                        e.uid: {"id": u.id, "name": u.name}
                        for u in system.users()
                        for e in self.events
                        if e.uid == u.id
                    }.values()
                )
                groups = list(
                    {
                        e.gid: {"id": g.id, "name": g.name}
                        for g in system.groups()
                        for e in self.events
                        if e.gid == g.id
                    }.values()
                )
                print("loaded events", self.events)
                GLib.idle_add(self.userList.load_store, users)
                GLib.idle_add(self.groupList.load_store, groups)
            except Exception as e:
                print("raised exception: ", e)

        self.userList.set_loading(True)
        self.groupList.set_loading(True)
        self.subjectList.get_ref().set_sensitive(False)
        self.objectList.get_ref().set_sensitive(False)
        print("executing process")
        self.executor.submit(process)

    def __all_list(self):
        box = Gtk.Box()
        box.set_border_width(10)
        box.add(
            Gtk.Label(label="Show something here that makes sense for the All tab??")
        )
        box.show_all()
        return box

    def __populate_acl_details(self, id, detailsFn):
        userDetails = self.get_object("userDetails")
        details = "\n".join(detailsFn(id).split(" ")) if id else ""
        userDetails.get_buffer().set_text(details)

    def __populate_subjects(self, id, compareFn):
        if not id:
            self.subjectList.get_ref().set_sensitive(False)
            self.subjectList.load_store([])
            return

        self.subjectList.get_ref().set_sensitive(True)
        subjects = list(
            {
                e.subject.file: e.subject for e in self.events if compareFn(id, e)
            }.values()
        )
        self.subjectList.load_store(subjects)

    def on_user_selection_changed(self, data):
        uid = data[1] if data else None
        self.__populate_acl_details(uid, acl.getUserDetails)
        self.__populate_subjects(uid, lambda uid, event: event.uid == uid)

    def on_group_selection_changed(self, data):
        gid = data[1] if data else None
        self.__populate_acl_details(gid, acl.getGroupDetails)
        self.__populate_subjects(gid, lambda gid, event: event.gid == gid)

    def on_subject_selection_changed(self, data):
        subjectDetails = self.get_object("subjectDetails")
        if not data:
            subjectDetails.get_buffer().set_text("")
            self.objectList.get_ref().set_sensitive(False)
            self.objectList.load_store([])
            return

        subjectDetails.get_buffer().set_text(fs.stat(data.file))
        self.objectList.get_ref().set_sensitive(True)
        objects = list(
            {
                e.object.file: e.object
                for e in self.events
                if e.subject.file == data.file
            }.values()
        )
        self.objectList.load_store(objects)

    def on_object_selection_changed(self, data):
        objectDetails = self.get_object("objectDetails")
        objectDetails.get_buffer().set_text(fs.stat(data.file) if data else "")
