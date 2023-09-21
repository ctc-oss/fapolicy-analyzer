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

import os
from fapolicy_analyzer import app_log_dir, app_data_dir, app_config_dir


def _app_dir_prefix(key):
    # Use default xdg locations if rust bindings built w/optional 'xdg' FEATURE.
    # i.e. FEATURES file contains 'xdg' string.
    dictSysFapaDefaults = {
        "_DATA_DIR_PREFIX": app_log_dir(),
        "_STATE_DIR_PREFIX": app_data_dir(),
        "_CONFIG_DIR_PREFIX": app_config_dir(),
    }

    app_tmp_dir = dictSysFapaDefaults[key]

    try:
        # Create if needed
        if not os.path.exists(app_tmp_dir):
            print(" Creating '{}' ".format(app_tmp_dir))
            os.makedirs(app_tmp_dir, 0o700)
    except Exception as e:
        print(
            "Warning: Directory creation of '{}' failed."
            "Using /tmp/".format(app_tmp_dir),
            e,
        )
        app_tmp_dir = "/tmp/"

    return app_tmp_dir


def app_state_dir_prefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_STATE_HOME
    directory, creates the directory if needed.
    """
    strAbsolutePath = os.path.join(_app_dir_prefix("_STATE_DIR_PREFIX"), strBaseName)
    return strAbsolutePath


def app_data_dir_prefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_DATA_HOME
    directory, creates the directory if needed.
    """
    strAbsolutePath = os.path.join(_app_dir_prefix("_DATA_DIR_PREFIX"), strBaseName)
    return strAbsolutePath


def app_config_dir_prefix(strBaseName):
    """Prefixes the file basename, strBaseName, with the XDG_CONFIG_HOME
    default directory, and verifies that it is readable by the effective user.
    """
    return os.path.join(_app_dir_prefix("_CONFIG_DIR_PREFIX"), strBaseName)
