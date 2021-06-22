from .ui_widget import UIWidget


class UnappliedChangesDialog(UIWidget):
    def __init__(self, parent=None):
        super().__init__()
        if parent:
            self.get_ref().set_transient_for(parent)
