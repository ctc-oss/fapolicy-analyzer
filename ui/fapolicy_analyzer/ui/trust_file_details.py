from .ui_widget import UIWidget


class TrustFileDetails(UIWidget):
    def get_content(self):
        return self.builder.get_object("trustFileDetails")

    def set_In_Database_View(self, text):
        self.builder.get_object("inDatabaseView").get_buffer().set_text(text)

    def set_On_File_System_View(self, text):
        self.builder.get_object("onFileSystemView").get_buffer().set_text(text)

    def set_trust_status(self, text):
        self.builder.get_object("fileTrustStatusView").get_buffer().set_text(text)
