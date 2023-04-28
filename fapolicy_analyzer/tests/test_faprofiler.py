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

import pytest
import os
from fapolicy_analyzer.ui.faprofiler import (
    FaProfSession,
    ProfSessionArgsStatus,
)


@pytest.mark.parametrize(
    "dictArgs", [
        # Populate target dictionary w/unexpected keys
        {
            "cmd": "Now.sh",
            "argBadText": "",
            "uid": os.getenv("USER"),
            "dirBadText": "/tmp",
            "env": "PATH=.:${PATH}",
        },
        # Populate target dictionary w/Missing keys
        {
            "cmd": "ls",
            "uid": os.getenv("USER"),
            "env": "",
        },
    ]
)
def test_faprofsession_init_w_bad_keys(dictArgs):
    with pytest.raises(KeyError):
        FaProfSession.validateArgs(dictArgs)


def test_faprofsession_path_env():
    dictArgs = {
        "cmd": "ls",
        "arg": "-ltr /tmp",
        "uid": os.getenv("USER"),
        "pwd": os.getenv("HOME"),
        "env": 'PATH=/tmp:$PATH, XX="xx"',
    }

    s = FaProfSession.which(dictArgs)
    assert os.path.basename(s) == dictArgs["cmd"]

    # directory may differ on different platforms; we only care that it's > 0
    assert os.path.dirname(s)


def test_validateArgs():
    dictArgs = {
        "cmd": "/usr/bin/ls",
        "arg": "-ltr /tmp",
        "uid": os.getenv("USER"),
        "pwd": os.getenv("HOME"),
        "env": "XYZ=123",
    }

    # Test w/good args; only OK key is in returned dict
    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 1
    assert ProfSessionArgsStatus.OK in dict_valid_args_return

    # Verify empty exec path is detected
    dictArgs["cmd"] = ""
    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 1
    assert ProfSessionArgsStatus.EXEC_EMPTY in dict_valid_args_return

    # Verify non-existent exec path is detected
    dictArgs["cmd"] = "/usr/bin/l"
    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 1
    assert ProfSessionArgsStatus.EXEC_DOESNT_EXIST in dict_valid_args_return

    # Verify non-executable exec path is detected
    dictArgs["cmd"] = os.getenv("HOME") + "/.bashrc"
    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 1
    assert ProfSessionArgsStatus.EXEC_NOT_EXEC in dict_valid_args_return
    dictArgs["cmd"] = "/usr/bin/ls"

    # Verify non-existent user is detected
    dictArgs["uid"] = "ooo"
    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 1
    assert ProfSessionArgsStatus.USER_DOESNT_EXIST in dict_valid_args_return
    dictArgs["uid"] = os.getenv("USER")

    # Verify non-existent pwd is detected
    dictArgs["pwd"] = os.getenv("HOME") + "/ng/"
    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 1
    assert ProfSessionArgsStatus.PWD_DOESNT_EXIST in dict_valid_args_return

    # Verify non-directory pwd is detected
    dictArgs["pwd"] = os.getenv("HOME") + "/.bashrc"
    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 1
    assert ProfSessionArgsStatus.PWD_ISNT_DIR in dict_valid_args_return

    # Verify multiple invalid fields are packed into returned dict
    dictArgs = {
        "cmd": "/usr/bin/l",
        "arg": "-ltr /tmp",
        "uid": "ooo",
        "pwd": os.getenv("HOME") + "/ng/",
        "env": "XYZ=123",
    }

    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 3
    assert ProfSessionArgsStatus.USER_DOESNT_EXIST in dict_valid_args_return
    assert ProfSessionArgsStatus.EXEC_DOESNT_EXIST in dict_valid_args_return
    assert ProfSessionArgsStatus.PWD_DOESNT_EXIST in dict_valid_args_return


@pytest.mark.parametrize(
    "dictArgs, expected_status", [
        (
            # Verify non-existent relative exec path is detected
            {
                "cmd": "Now.sh",
                "arg": "",
                "uid": os.getenv("USER"),
                "pwd": "/tmp",
                "env": "PATH=.:${PATH}",
            },
            ProfSessionArgsStatus.EXEC_NOT_FOUND,
        ),
        (
            # Test w/good args; only OK key is in returned dict
            {
                "cmd": "ls",
                "arg": "",
                "uid": os.getenv("USER"),
                "pwd": os.getenv("HOME"),
                "env": "",
            },
            ProfSessionArgsStatus.OK,
        ),
    ]
)
def test_validateArgs_relative_exec(dictArgs, expected_status):
    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 1
    assert expected_status in dict_valid_args_return


@pytest.mark.parametrize(
    "dictArgs, expected_status", [
        (
            # Test w/good env var string; only OK key is in returned dict
            {
                "cmd": "ls",
                "arg": "",
                "uid": os.getenv("USER"),
                "pwd": os.getenv("HOME"),
                "env": "PATH=$PATH:.,A=a",
            },
            ProfSessionArgsStatus.OK,
        ),
        (
            # Test w/bad env vars (not KV pair) ENV_VARS_FORMATING is returned
            {
                "cmd": "ls",
                "arg": "",
                "uid": os.getenv("USER"),
                "pwd": os.getenv("HOME"),
                "env": "PATH=$PATH:.,A",
            },
            ProfSessionArgsStatus.ENV_VARS_FORMATING,
        ),
        (
            # Test w/bad env vars (key name) ENV_VARS_FORMATING is returned
            {
                "cmd": "ls",
                "arg": "",
                "uid": os.getenv("USER"),
                "pwd": os.getenv("HOME"),
                "env": "PATH=$PATH:.,A-B=1",
            },
            ProfSessionArgsStatus.ENV_VARS_FORMATING,
        ),
        (
            # Test w/bad env vars (missing key) ENV_VARS_FORMATING is returned
            {
                "cmd": "ls",
                "arg": "",
                "uid": os.getenv("USER"),
                "pwd": os.getenv("HOME"),
                "env": "PATH=$PATH:.,=1",
            },
            ProfSessionArgsStatus.ENV_VARS_FORMATING,
        ),
        (
            # Test w/bad env vars (empty key) ENV_VARS_FORMATING is returned
            {
                "cmd": "ls",
                "arg": "",
                "uid": os.getenv("USER"),
                "pwd": os.getenv("HOME"),
                "env": "PATH=$PATH:.," "=1",
            },
            ProfSessionArgsStatus.ENV_VARS_FORMATING,
        ),
    ]
)
def test_validateArgs_env_vars(dictArgs, expected_status):
    dict_valid_args_return = FaProfSession.validateArgs(dictArgs)
    assert len(dict_valid_args_return) == 1
    assert expected_status in dict_valid_args_return
