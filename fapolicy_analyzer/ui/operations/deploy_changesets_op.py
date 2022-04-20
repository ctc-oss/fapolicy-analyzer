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
from typing import Mapping, Sequence, Tuple

import gi
from fapolicy_analyzer import Changeset
from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    clear_changesets,
    deploy_ancillary_trust,
    restore_system_checkpoint,
    set_system_checkpoint,
)
from fapolicy_analyzer.ui.confirm_info_dialog import ConfirmInfoDialog
from fapolicy_analyzer.ui.deploy_confirm_dialog import DeployConfirmDialog
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.ui.strings import (
    ANY_FILES_FILTER_LABEL,
    DEPLOY_ANCILLARY_ERROR_MSG,
    DEPLOY_ANCILLARY_SUCCESSFUL_MSG,
    FA_ARCHIVE_FILES_FILTER_LABEL,
    SAVE_AS_FILE_LABEL,
)
from fapolicy_analyzer.util.fapd_dbase import fapd_dbase_snapshot

from .ui_operation import UIOperation

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
        self.__subscription = get_system_feature().subscribe(on_next=self.__on_next)

    def __changesets_to_path_action_pairs(
        self,
        changesets: Changeset,
    ) -> Sequence[Tuple[str, str]]:
        """Converts to list of human-readable undeployed path/operation pairs"""
        return [t for e in changesets for t in e.get_path_action_map().items()]

    def __get_fapd_archive_file_name(self) -> str:
        """Display a file chooser dialog to specify the output archive file."""
        fcd = _FapdArchiveFileChooserDialog(self.__window)
        response = fcd.run()
        fcd.hide()
        strFilename = fcd.get_filename() if response == Gtk.ResponseType.OK else None
        fcd.destroy()
        return strFilename

    def __display_deploy_confirmation_dialog(self):
        deployConfirmDialog = DeployConfirmDialog(self.__window).get_ref()
        revert_resp = deployConfirmDialog.run()
        deployConfirmDialog.hide()
        if revert_resp == Gtk.ResponseType.YES:
            dispatch(set_system_checkpoint())
            dispatch(clear_changesets())
        else:
            dispatch(restore_system_checkpoint())

    def __on_next(self, system: Mapping[str, any]):
        trustState = system.get("ancillary_trust")

        if trustState.error and self.__deploying:
            self.__deploying = False
            logging.error("%s: %s", DEPLOY_ANCILLARY_ERROR_MSG, trustState.error)
            dispatch(
                add_notification(DEPLOY_ANCILLARY_ERROR_MSG, NotificationType.ERROR)
            )
        elif self.__deploying and trustState.deployed:
            self.__deploying = False
            dispatch(
                add_notification(
                    DEPLOY_ANCILLARY_SUCCESSFUL_MSG,
                    NotificationType.SUCCESS,
                )
            )
            self.__display_deploy_confirmation_dialog()

    def get_text(self) -> str:
        return _("Deploy Changes")

    def get_icon(self) -> str:
        return "system-software-update"

    def run(self, changesets: Changeset):
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
        listPathActionTuples = self.__changesets_to_path_action_pairs(changesets)
        logging.debug(listPathActionTuples)
        dlgDeployList = ConfirmInfoDialog(self.__window, listPathActionTuples)
        confirm_resp = dlgDeployList.run()
        dlgDeployList.hide()

        if confirm_resp == Gtk.ResponseType.YES:
            # Invoke a file chooser dlg and generate the fapd state tarball
            if dlgDeployList.get_save_state():
                strArchiveName = self.__get_fapd_archive_file_name()
                if strArchiveName:
                    fapd_dbase_snapshot(strArchiveName)

            logging.debug("Deploying...")
            self.__deploying = True
            dispatch((deploy_ancillary_trust()))

        dlgDeployList.destroy()

    def dispose(self):
        """
        Closes the feature subscriptions
        """
        if self.__subscription:
            logging.debug(
                "disposing of subscription for class {}".format(self.__class__.__name__)
            )
            self.__subscription.dispose()
