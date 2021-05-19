import gi
import re

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from os import path
from events import Events
from .ui_widget import UIWidget
from .confirmation_dialog import ConfirmDialog


class TrustFileList(UIWidget, Events):
    __events__ = ["file_selection_change", "files_added"]

    def __init__(self, trust_func, markup_func=None, read_only=False):
        def setup_trustView():
            self.trustView = self.get_object("trustView")
            trustCell = Gtk.CellRendererText()
            trustCell.set_property("background", "light gray")
            trustColumn = Gtk.TreeViewColumn("Trust", trustCell, markup=0)
            trustColumn.set_sort_column_id(0)
            self.trustView.append_column(trustColumn)
            fileColumn = Gtk.TreeViewColumn(
                "File", Gtk.CellRendererText(), text=1, cell_background=3
            )
            fileColumn.set_sort_column_id(1)
            self.trustView.append_column(fileColumn)

        def setup_loader():
            loader = self.get_object("trustViewLoader")
            loader.set_from_animation(
                GdkPixbuf.PixbufAnimation.new_from_file(
                    self.absolute_file_path("../../resources/filled_fading_balls.gif")
                )
            )

        UIWidget.__init__(self)
        Events.__init__(self)
        self.markup_func = markup_func
        self.trustFileList = self.builder.get_object("trustFileList")

        setup_trustView()
        setup_loader()

        if read_only:
            addBtn = self.get_object("addBtn")
            addBtn.get_parent().remove(addBtn)

        self.refresh(trust_func)

    def __load_trust_store(self, trust):
        trustStore = Gtk.ListStore(str, str, object, str)
        for i, t in enumerate(trust):
            status, *rest = (
                self.markup_func(t.status) if self.markup_func else (t.status,)
            )
            bgColor = rest[0] if rest else "white"
            trustStore.append([status, t.path, t, bgColor])

        self.trustViewFilter = trustStore.filter_new()
        self.trustViewFilter.set_visible_func(self.__filter_trust_view)
        self.trustView.set_model(Gtk.TreeModelSort(model=self.trustViewFilter))
        self.trustView.get_selection().connect(
            "changed", self.on_trust_view_selection_changed
        )
        self.__set_loading(False)

    def __filter_trust_view(self, model, iter, data):
        filter = self.builder.get_object("trustViewSearch").get_text()
        return True if not filter else filter in model[iter][1]

    def __set_loading(self, loading):
        viewSwitcher = self.builder.get_object("trustViewStack")
        trustViewSearch = self.builder.get_object("trustViewSearch")
        if loading:
            viewSwitcher.set_visible_child_name("trustViewLoader")
            trustViewSearch.set_sensitive(False)
        else:
            viewSwitcher.set_visible_child_name("trustView")
            trustViewSearch.set_sensitive(True)

    def get_content(self):
        return self.trustFileList

    def refresh(self, trust_func):
        self.__set_loading(True)
        trust_func(self.__load_trust_store)

    def on_trust_view_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        trust = model[treeiter][2] if treeiter is not None else {}
        self.file_selection_change(trust)

    def on_search_changed(self, search):
        self.trustViewFilter.refilter()

    def on_addBtn_clicked(self, *args):
        fcd = Gtk.FileChooserDialog(
            "Add File",
            self.trustFileList.get_toplevel(),
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_ADD,
                Gtk.ResponseType.OK,
            ),
        )
        fcd.set_select_multiple(True)
        response = fcd.run()
        fcd.hide()
        if response == Gtk.ResponseType.OK:
            files = [f for f in fcd.get_filenames() if path.isfile(f)]

            ##### Filter to address fapolicyd embeded whitspace in path issue
            #     Current fapolicyd VT.B.D. When fixed remove this block
            #
            # Detect and remove file paths w/embedded spaces. Alert user w/dlg
            print ("Filtering out paths with embedded whitespace")
            listTmp = []
            for e in files:
                if not re.search(r"\s", e):
                    listTmp.append(e)
                else:
                    dlgWhitespaceInfo = Gtk.MessageDialog(
                        transient_for=self.trustFileList.get_toplevel(),
                        flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text="File path contains embedded whitespace.",
                    )
                    dlgWhitespaceInfo.format_secondary_text(
                        f"{e}, contains whitespace.\nfapolicyd "+
                        "currently does not support paths containing spaces.\n"+
                        "\nPath will not be added to the Trusted Files List."+
                        "(fapolicyd: VTBD)"
                    )
                    dlgWhitespaceInfo.run()
                    dlgWhitespaceInfo.destroy()
            files = listTmp
            #     Remove this filter block if fapolicyd bug #TBD is fixed
            #################################################################
            
            if files:
                self.files_added(files)
        fcd.destroy()
