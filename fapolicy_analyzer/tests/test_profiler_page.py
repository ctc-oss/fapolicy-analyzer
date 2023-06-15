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
import datetime

import gi
import pytest
import os

from callee import InstanceOf, Attrs
from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import (
    PROFILING_KILL_REQUEST,
    PROFILER_CLEAR_STATE_CMD,
    START_PROFILING_REQUEST,
    ADD_NOTIFICATION,
)
from fapolicy_analyzer.ui.reducers.profiler_reducer import profiler_state, ProfilerState
from fapolicy_analyzer.ui.store import init_store
from mocks import mock_System
from fapolicy_analyzer.ui.profiler_page import (
    ProfilerPage,
    FaProfArgs,
    ProfArgsStatus,
    _expand_user_home,
    _args_user_home_expansion,
)
from fapolicy_analyzer.ui.fapd_manager import FapdManager

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.profiler_page.dispatch")


@pytest.fixture
def widget(mocker):
    init_store(mock_System())
    return ProfilerPage(FapdManager(False))


def test_creates_widget(widget):
    assert type(widget.get_ref()) is Gtk.Box


def get_output_text(widget):
    textBuffer = widget.get_object("profilerOutput").get_buffer()
    return textBuffer.get_text(
        textBuffer.get_start_iter(), textBuffer.get_end_iter(), True
    )


def test_get_entry_dict(widget):
    widget.update_input_fields("foo", "root", "/tmp", None)
    conf = widget.get_entry_dict()
    assert conf.get("cmd") == "foo"
    assert conf.get("uid") == "root"
    assert conf.get("pwd") == "/tmp"
    assert conf.get("env") is None


def test_make_profiling_args(widget):
    widget.update_input_fields("ls", "root", "/tmp", "FOO=BAR,BAZ=BOO")
    profiling_args = widget._make_profiling_args()
    assert profiling_args.get("cmd") == "ls"
    assert profiling_args.get("uid") == "root"
    assert profiling_args.get("pwd") == "/tmp"
    assert profiling_args.get("env") == "FOO=BAR,BAZ=BOO"
    assert profiling_args.get("env_dict") == {"FOO": "BAR", "BAZ": "BOO"}


def test_make_profiling_args_w_path_env_var(widget):
    widget.update_input_fields("ls", "root", "/tmp", "FOO=BAR, PATH=$PATH:.")
    profiling_args = widget._make_profiling_args()
    expected_path = f"{os.getenv('PATH')}:/tmp"
    assert profiling_args.get("cmd") == "ls"
    assert profiling_args.get("uid") == "root"
    assert profiling_args.get("pwd") == "/tmp"
    assert profiling_args.get("env") == "FOO=BAR, PATH=$PATH:."
    assert profiling_args.get("env_dict") == {"FOO": "BAR", "PATH": expected_path}


def test_stop_profiling_click(widget, mock_dispatch):
    widget.on_stop_clicked()
    assert widget.can_stop is False
    mock_dispatch.assert_called_with(
        InstanceOf(Action) & Attrs(type=PROFILING_KILL_REQUEST, payload=None)
    )


def test_clear_state_click(widget, mock_dispatch):
    widget.update_input_fields("foo", "root", "/tmp", None)
    widget.on_clear_button_clicked()
    assert widget.get_cmd_text() is None
    assert widget.get_arg_text() is None
    assert widget.get_pwd_text() is None
    assert widget.get_env_text() is None
    mock_dispatch.assert_called_with(
        InstanceOf(Action) & Attrs(type=PROFILER_CLEAR_STATE_CMD, payload=None)
    )


def test_on_tick(widget):
    state = profiler_state(ProfilerState, cmd="foo", pid=999, duration=42)
    t = datetime.timedelta(seconds=state.duration) if state.duration else ""
    expected = f"{state.pid}: Executing {state.cmd} {t}"
    widget.handle_tick(state)
    assert get_output_text(widget) == expected


def test_start_click(widget, mock_dispatch):
    widget.update_input_fields("ls", "root", "/tmp", None)
    profiling_args = widget._make_profiling_args()

    widget.on_start_clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action) & Attrs(type=START_PROFILING_REQUEST, payload=profiling_args)
    )


def test_start_click_with_env(widget, mock_dispatch):
    widget.update_input_fields("ls", "root", "/tmp", "FOO=BAR,BAZ=BOO")
    profiling_args = widget._make_profiling_args()

    widget.on_start_clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action) & Attrs(type=START_PROFILING_REQUEST, payload=profiling_args)
    )


def test_start_click_with_bad_cmd(widget, mock_dispatch):
    widget.update_input_fields("xX_Xx", "root", "/tmp", "FOO=BAR,BAZ=BOO")
    widget.on_start_clicked()
    mock_dispatch.assert_called_with(InstanceOf(Action) & Attrs(type=ADD_NOTIFICATION))


def test_start_click_with_bad_env(widget, mock_dispatch):
    widget.update_input_fields("ls", "root", "/tmp", "FOO")
    widget.on_start_clicked()
    mock_dispatch.assert_called_with(InstanceOf(Action) & Attrs(type=ADD_NOTIFICATION))


def test_start_click_with_bad_uid(widget, mock_dispatch):
    widget.update_input_fields("ls", "foooooo", "/tmp", "FOO")
    widget.on_start_clicked()
    mock_dispatch.assert_called_with(InstanceOf(Action) & Attrs(type=ADD_NOTIFICATION))


###########################################################################
# Profiler arg specific unit tests
def test_validateArgs():
    test_user = os.getenv("USER")
    test_home = os.getenv("HOME")
    dictArgs = {
        "cmd": "/usr/bin/ls",
        "arg": "-ltr /tmp",
        "uid": test_user,
        "pwd": test_home,
        "env": "XYZ=123",
    }

    # Test w/good args; only OK key is in returned dict
    dict_in = dict(dictArgs)
    dict_valid_args_return = FaProfArgs.validateArgs(dict_in)
    assert len(dict_valid_args_return) == 1
    assert ProfArgsStatus.OK in dict_valid_args_return

    # Verify empty exec path is detected
    dict_in = dict(dictArgs)
    dict_in["cmd"] = ""
    dict_valid_args_return = FaProfArgs.validateArgs(dict_in)
    assert len(dict_valid_args_return) == 1
    assert ProfArgsStatus.EXEC_EMPTY in dict_valid_args_return

    # Verify non-existent exec path is detected
    dict_in = dict(dictArgs)
    dict_in["cmd"] = "/usr/bin/l"
    dict_valid_args_return = FaProfArgs.validateArgs(dict_in)
    assert len(dict_valid_args_return) == 1
    assert ProfArgsStatus.EXEC_DOESNT_EXIST in dict_valid_args_return

    # Verify non-executable exec path is detected
    dict_in = dict(dictArgs)
    dict_in["cmd"] = os.getenv("HOME") + "/.bashrc"
    dict_valid_args_return = FaProfArgs.validateArgs(dict_in)
    assert len(dict_valid_args_return) == 1
    assert ProfArgsStatus.EXEC_NOT_EXEC in dict_valid_args_return

    # Verify non-existent user is detected
    dict_in = dict(dictArgs)
    dict_in["uid"] = "ooo"
    dict_valid_args_return = FaProfArgs.validateArgs(dict_in)
    assert len(dict_valid_args_return) == 1
    assert ProfArgsStatus.USER_DOESNT_EXIST in dict_valid_args_return

    # Verify non-existent pwd is detected
    dict_in = dict(dictArgs)
    dict_in["pwd"] = os.getenv("HOME") + "/ng/"
    dict_valid_args_return = FaProfArgs.validateArgs(dict_in)
    assert len(dict_valid_args_return) == 1
    assert ProfArgsStatus.PWD_DOESNT_EXIST in dict_valid_args_return

    # Verify non-directory pwd is detected
    dict_in["pwd"] = os.getenv("HOME") + "/.bashrc"
    dict_valid_args_return = FaProfArgs.validateArgs(dict_in)
    assert len(dict_valid_args_return) == 1
    assert ProfArgsStatus.PWD_ISNT_DIR in dict_valid_args_return

    # Verify multiple invalid fields are packed into returned dict
    dict_in = {
        "cmd": "/usr/bin/l",
        "arg": "-ltr /tmp",
        "uid": "ooo",
        "pwd": os.getenv("HOME") + "/ng/",
        "env": "XYZ=123",
    }

    dict_valid_args_return = FaProfArgs.validateArgs(dict_in)
    assert len(dict_valid_args_return) == 3
    assert ProfArgsStatus.USER_DOESNT_EXIST in dict_valid_args_return
    assert ProfArgsStatus.EXEC_DOESNT_EXIST in dict_valid_args_return
    assert ProfArgsStatus.PWD_DOESNT_EXIST in dict_valid_args_return


def test_throwOnInvalidSessionArgs():
    dict_in = {
        "cmd": "/usr/bin/l",
        "arg": "-ltr /tmp",
        "uid": "ooo",
        "pwd": os.getenv("HOME") + "/ng/",
        "env": "XYZ=123",
    }

    # Should throw a RuntimeError
    with pytest.raises(RuntimeError):
        FaProfArgs.throwOnInvalidSessionArgs(dict_in)


def test_expand_user_home():
    user = "testuser"
    homedir = "/home/testuser"
    str_in = r"A generic string w/user=$USER and home=$HOME"

    str_return = _expand_user_home(str_in, user, homedir)
    assert str_return == f"A generic string w/user={user} and home={homedir}"

    # Input string should not expand
    str_in = r"A non-expandable string w/user = USER and home = HOME"

    str_return = _expand_user_home(str_in, user, homedir)
    assert str_return == str_in


def test_args_user_home_expansion():
    test_user = os.getenv("USER")
    test_home = os.getenv("HOME")
    dictArgs = {
        "cmd": "/usr/bin/ls",
        "arg": "-ltr /tmp",
        "uid": test_user,
        "pwd": test_home,
        "env": "x=f{test_user}",
    }

    # No modification
    dict_in = dict(dictArgs)
    dict_return = _args_user_home_expansion(dict_in)
    assert dict_in == dict_return

    # Insert expandable $USER and $HOME text with/without braces
    dict_in = dict(dictArgs)
    dict_in["pwd"] = "$HOME"
    dict_in["env"] = "x=$USER"
    dict_in["arg"] = "$HOME"
    dict_return = _args_user_home_expansion(dict_in)
    assert dict_in != dict_return
    assert dict_return["pwd"] == test_home
    assert dict_return["env"] == f"x={test_user}"
    assert dict_return["arg"] == test_home

    dict_in = dict(dictArgs)
    dict_in["pwd"] = "${HOME}"
    dict_in["env"] = "x=${USER}"
    dict_in["arg"] = "${HOME}"
    dict_return = _args_user_home_expansion(dict_in)
    assert dict_in != dict_return
    assert dict_return["pwd"] == test_home
    assert dict_return["env"] == f"x={test_user}"
    assert dict_return["arg"] == test_home

    # Insert non-expandable $USR and $HMOE text
    dict_in = dict(dictArgs)
    dict_in["pwd"] = "$HMOE"
    dict_in["env"] = "x=$USR"
    dict_in["arg"] = "$HME"
    dict_return = _args_user_home_expansion(dict_in)
    assert dict_in == dict_return

    # Insert non-expandable $USR and $HMOE text w/braces
    dict_in["pwd"] = "${HMOE}"
    dict_in["env"] = "x=${USR}"
    dict_in["arg"] = "${HME}"
    dict_in = dict(dictArgs)
    dict_return = _args_user_home_expansion(dict_in)
    assert dict_in == dict_return

    # No user. defaults to euid's username and home
    dict_in = dict(dictArgs)
    dict_in["uid"] = None
    dict_in["pwd"] = "$HOME"
    dict_in["env"] = "x=$USER"

    dict_return = _args_user_home_expansion(dict_in)
    assert dict_in != dict_return
    assert dict_return["pwd"] == test_home
    assert dict_return["env"] == f"x={test_user}"


@pytest.mark.parametrize(
    "dictArgs",
    [
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
    ],
)
def test_invalid_session_args_w_bad_keys(dictArgs):
    with pytest.raises(KeyError):
        FaProfArgs.throwOnInvalidSessionArgs(dictArgs)


def test_comma_delimited_kv_string_to_dict():
    # Test w/good sequence of comma separated k=v pairs
    str_in = "A=a, B=b, C=c"
    dict_expected = {"A": "a", "B": "b", "C": "c"}
    dict_out = FaProfArgs.comma_delimited_kv_string_to_dict(str_in)
    assert dict_expected == dict_out
