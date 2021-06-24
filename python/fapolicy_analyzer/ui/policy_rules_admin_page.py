import gi

# import ui.strings as strings

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from .object_list import ObjectList
from .string_list import StringList
from .strings import GROUP_LABEL, GROUPS_LABEL, USER_LABEL, USERS_LABEL
from .subject_list import SubjectList
from .ui_widget import UIWidget
from util import users, fs


class PolicyRulesAdminPage(UIWidget):
    def __init__(self):
        super().__init__()

        userTabs = self.get_object("userTabs")
        userTabs.append_page(
            self.__user_list().get_ref(),
            Gtk.Label(label="User"),
        )
        userTabs.append_page(
            self.__group_list().get_ref(),
            Gtk.Label(label="Group"),
        )
        userTabs.append_page(
            self.__all_list(),
            Gtk.Label(label="All"),
        )

        subjectTabs = self.get_object("subjectTabs")
        subjectList = SubjectList()
        subjectList.subject_selection_changed += self.on_subject_selection_changed
        subjectTabs.append_page(subjectList.get_ref(), Gtk.Label(label="Subject"))

        objectTabs = self.get_object("objectTabs")
        objectList = ObjectList()
        objectList.object_selection_changed += self.on_object_selection_changed
        objectTabs.append_page(objectList.get_ref(), Gtk.Label(label="Object"))

    def __user_list(self):
        userList = StringList(label=USER_LABEL, label_plural=USERS_LABEL)
        userList.selection_changed = self.on_user_selection_changed
        userList.load_store(users.getAllUsers())
        return userList

    def __group_list(self):
        groupList = StringList(label=GROUP_LABEL, label_plural=GROUPS_LABEL)
        groupList.selection_changed = self.on_group_selection_changed
        groupList.load_store(users.getAllGroups())
        return groupList

    def __all_list(self):
        box = Gtk.Box()
        box.set_border_width(10)
        box.add(
            Gtk.Label(label="Show something here that makes sense for the All tab??")
        )
        box.show_all()
        return box

    def on_user_selection_changed(self, data):
        details = "\n".join(users.getUserDetails(data[0]).split(" "))
        self.get_object("userDetails").get_buffer().set_text(details)

    def on_group_selection_changed(self, data):
        details = "\n".join(users.getGroupDetails(data[0]).split(" "))
        self.get_object("userDetails").get_buffer().set_text(details)

    def on_subject_selection_changed(self, data):
        self.get_object("subjectDetails").get_buffer().set_text(
            fs.stat(data.get("path"))
        )

    def on_object_selection_changed(self, data):
        self.get_object("objectDetails").get_buffer().set_text(
            fs.stat(data.get("path"))
        )
