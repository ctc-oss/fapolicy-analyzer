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

import logging
from locale import gettext as _
from typing import Any, Sequence

import gi
from fapolicy_analyzer import System
from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    clear_changesets,
    deploy_system,
    restore_system_checkpoint,
    set_system_checkpoint,
)
from fapolicy_analyzer.ui.changeset_wrapper import Changeset
from fapolicy_analyzer.ui.confirm_deployment_dialog import ConfirmDeploymentDialog
from fapolicy_analyzer.ui.deploy_revert_dialog import DeployRevertDialog
from fapolicy_analyzer.ui.operations.ui_operation import UIOperation
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.ui.strings import (
    ANY_FILES_FILTER_LABEL,
    DEPLOY_SYSTEM_ERROR_MSG,
    DEPLOY_SYSTEM_SUCCESSFUL_MSG,
    FA_ARCHIVE_FILES_FILTER_LABEL,
    REVERT_SYSTEM_SUCCESSFUL_MSG,
    SAVE_AS_FILE_LABEL,
    UNSAVED_DIALOG_MSG,
)
from fapolicy_analyzer.util.fapd_dbase import fapd_dbase_snapshot

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


class _FapdArchiveFileChooserDialog(Gtk.FileChooserDialog):
    def __init__(self, parent):
        super().__init__(
            title=SAVE_AS_FILE_LABEL,
            transient_for=parent,
            action=Gtk.FileChooserAction.SAVE,
        )
        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )
        self.set_do_overwrite_confirmation(True)

        fileFilterTgz = Gtk.FileFilter()
        fileFilterTgz.set_name(FA_ARCHIVE_FILES_FILTER_LABEL)
        fileFilterTgz.add_pattern("*.tgz")
        self.add_filter(fileFilterTgz)

        fileFilterAny = Gtk.FileFilter()
        fileFilterAny.set_name(ANY_FILES_FILTER_LABEL)
        fileFilterAny.add_pattern("*")
        self.add_filter(fileFilterAny)
        self.show_all()


class DeployChangesetsOp(UIOperation):
    """Encapsulates the operation of deploying changesets.

    Attributes
    ----------
    parentWindow : Gtk.Window, optional
        top level window to attach dialog windows to

    Methods
    -------
    deploy(changesets=None):
        deploys the given changesets

    To ensure proper cleanup it should be used within a with statement block.

    Example:
    with DeployChangesetsOp(parentWindow) as op:
        op.deploy(changesets)
    """

    def __init__(self, parentWindow: Gtk.Window = None) -> None:
        self.__window = parentWindow
        self.__deploying = False
        self.__reverting = False
        self.__subscription = get_system_feature().subscribe(on_next=self.__on_next)

    def __get_fapd_archive_file_name(self) -> str:
        """Display a file chooser dialog to specify the output archive file."""
        fcd = _FapdArchiveFileChooserDialog(self.__window)
        response = fcd.run()
        fcd.hide()
        strFilename = fcd.get_filename() if response == Gtk.ResponseType.OK else None
        fcd.destroy()
        return strFilename

    def __display_deploy_revert_dialog(self):
        deployConfirmDialog = DeployRevertDialog(self.__window).get_ref()
        revert_resp = deployConfirmDialog.run()
        deployConfirmDialog.hide()
        if revert_resp == Gtk.ResponseType.YES:
            dispatch(set_system_checkpoint())
            dispatch(clear_changesets())
        else:
            self.__reverting = True
            dispatch(restore_system_checkpoint())

    def __on_next(self, system: Any):
        systemState = system.get("system")
        text_state = system.get("rules_text")
        self.__rules_text = text_state.rules_text if text_state else ""
        self.__modified_rules_text = text_state.modified_rules_text if text_state else ""
        if systemState.error and self.__deploying:
            self.__deploying = False
            logging.error("%s: %s", DEPLOY_SYSTEM_ERROR_MSG, systemState.error)
            dispatch(add_notification(DEPLOY_SYSTEM_ERROR_MSG, NotificationType.ERROR))
        elif self.__deploying and systemState.deployed:
            self.__deploying = False
            dispatch(
                add_notification(
                    DEPLOY_SYSTEM_SUCCESSFUL_MSG,
                    NotificationType.SUCCESS,
                )
            )
            self.__display_deploy_revert_dialog()
        elif self.__reverting and systemState.system == systemState.checkpoint:
            self.__reverting = False
            dispatch(
                add_notification(
                    REVERT_SYSTEM_SUCCESSFUL_MSG,
                    NotificationType.SUCCESS,
                )
            )

    def get_text(self) -> str:
        return _("Deploy Changes")

    def get_icon(self) -> str:
        return "system-software-update"

    def run(self, changesets: Sequence[Changeset], system: System, checkpoint: System):
        """
        Deploys the given changesets.

        Parameters
        ----------
        changesets: fapolicy_analyze.Changeset
            Changesets to deploy

        Returns
        -------
        None
        """

        rules = (
            bool(self.__modified_rules_text)
            and self.__modified_rules_text != self.__rules_text
        )
        if rules:
            unsaved_rule_dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text=UNSAVED_DIALOG_MSG,
            )
            unsaved_resp = unsaved_rule_dialog.run()
            unsaved_rule_dialog.destroy()
            if unsaved_resp == Gtk.ResponseType.CANCEL:
                return

        dlgDeployList = ConfirmDeploymentDialog(
            changesets, system, checkpoint, parent=self.__window
        )
        confirm_resp = dlgDeployList.get_ref().run()
        dlgDeployList.get_ref().hide()

        if confirm_resp == Gtk.ResponseType.YES:
            # Invoke a file chooser dlg and generate the fapd state tarball
            if dlgDeployList.get_save_state():
                strArchiveName = self.__get_fapd_archive_file_name()
                if strArchiveName:
                    fapd_dbase_snapshot(strArchiveName)

            logging.debug("Deploying...")
            self.__deploying = True
            dispatch((deploy_system()))

        dlgDeployList.get_ref().destroy()

    def dispose(self):
        """
        Closes the feature subscriptions
        """
        if self.__subscription:
            logging.debug(
                "disposing of subscription for class {}".format(self.__class__.__name__)
            )
            self.__subscription.dispose()
