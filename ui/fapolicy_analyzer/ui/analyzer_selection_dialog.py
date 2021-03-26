from enum import Enum
from .ui_widget import UIWidget


class ANALYZER_SELECTION(Enum):
    TRUST_DATABASE_ADMIN = 0
    SCAN_SYSTEM = 1
    ANALYZE_FROM_AUDIT = 2


class AnalyzerSelectionDialog(UIWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.dialog = self.builder.get_object("analyzerSelectionDialog")
        if parent:
            self.dialog.set_transient_for(parent)

    def get_content(self):
        return self.dialog
