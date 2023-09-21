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

import glob
import json
import os
import time
from datetime import datetime as DT
from unittest.mock import MagicMock, call, mock_open

import pytest
from callee import Attr, EndsWith, InstanceOf, StartsWith
from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import (
    ADD_NOTIFICATION,
    APPLY_CHANGESETS,
    CLEAR_CHANGESETS,
    RESTORE_SYSTEM_CHECKPOINT,
)
from fapolicy_analyzer.ui.changeset_wrapper import RuleChangeset, TrustChangeset
from fapolicy_analyzer.ui.session_manager import SessionManager

import context  # noqa: F401

test_changes = [
    "foo rules",
    {
        "/data_space/this/is/a/longer/path/now_is_the_time.txt": "Del",
        "/data_space/Integration.json": "Add",
    },
]


test_json = json.dumps(
    test_changes,
    sort_keys=True,
    indent=4,
)

test_changesets = [RuleChangeset(), TrustChangeset()]
test_changesets[0].parse("foo rules")
test_changesets[1].delete("/data_space/this/is/a/longer/path/now_is_the_time.txt")
test_changesets[1].add("/data_space/Integration.json")


def mock_changesets_state(changesets=test_changesets, error=False):
    return MagicMock(changesets=changesets, error=error)


@pytest.fixture
def uut():
    sessionManager = SessionManager()
    sessionManager.set_autosave_enable(False)
    sessionManager.set_autosave_filename("/tmp/UnitTestSession")
    yield sessionManager
    sessionManager.cleanup()


@pytest.fixture
def uut_autosave_enabled():
    sessionManager = SessionManager()
    sessionManager.set_autosave_enable(True)
    yield sessionManager
    sessionManager.cleanup()


@pytest.fixture
def autosaved_files():
    with open("/tmp/FaCurrentSession.tmp_20210803_130622_059045.json", "w") as fp0:
        fp0.write(f"""[{json.dumps(test_changes[0], sort_keys=True, indent=4)}]""")

    with open("/tmp/FaCurrentSession.tmp_20210803_130622_065690.json", "w") as fp1:
        fp1.write(json.dumps(test_changes, sort_keys=True, indent=4))

    # yields  a list of the autosaved files
    yield [
        "/tmp/FaCurrentSession.tmp_20210803_130622_065690.json",
        "/tmp/FaCurrentSession.tmp_20210803_130622_059045.json",
    ]

    # Clean up the filesystem
    os.remove("/tmp/FaCurrentSession.tmp_20210803_130622_059045.json")
    os.remove("/tmp/FaCurrentSession.tmp_20210803_130622_065690.json")


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.session_manager.dispatch")


# ######################## Session Serialization #####################
def test_open_edit_session(uut, mock_dispatch, mocker):
    mocker.patch("builtins.open", mock_open(read_data=test_json))
    uut.open_edit_session("foo")

    mock_dispatch.assert_called_with(Attr(type=APPLY_CHANGESETS))

    # verify changesets
    expected = test_changes
    # parse changesets to json string to compare
    args, _ = mock_dispatch.call_args
    actual = [
        {path: action for path, action in c.serialize().items()}
        if isinstance(c, TrustChangeset)
        else c.serialize()
        for c in args[0].payload
    ]

    assert actual == expected


def test_open_edit_session_w_exception(uut, mock_dispatch, mocker):
    mockFunc = mocker.patch(
        "fapolicy_analyzer.ui.session_manager.json.load",
        side_effect=lambda: IOError("foo"),
    )

    mocker.patch("builtins.open", mock_open())
    uut.open_edit_session("foo")

    mockFunc.assert_called()
    mock_dispatch.assert_called_with(Attr(type=ADD_NOTIFICATION))


def test_save_edit_session(uut, mocker):
    mockFile = mocker.patch("builtins.open", mock_open())
    uut.save_edit_session(test_changesets, "foo")

    mockFile.assert_called_once_with("foo", "w")
    # we need to parse the json written out to the mock object
    actual = "".join(
        [args[0] for name, args, _ in mockFile.mock_calls if name == "().write"]
    )
    expected = test_json
    assert actual == expected


# ########################### Autosave Sessions #################
def test_autosave_edit_session(uut_autosave_enabled, mocker):
    mockFile = mocker.patch("builtins.open", mock_open())
    uut_autosave_enabled.on_next_system({"changesets": mock_changesets_state()})

    mockFile.assert_called_once_with(
        StartsWith(uut_autosave_enabled._SessionManager__tmpFileBasename)
        & EndsWith(".json"),
        "w",
    )
    # we need to parse the json written out to the mock object
    actual = "".join(
        [args[0] for name, args, _ in mockFile.mock_calls if name == "().write"]
    )
    expected = test_json
    assert actual == expected


def test_autosave_edit_session_w_exception(mocker, uut_autosave_enabled):
    # Create a mock that throw an exception side-effect
    mockFunc = mocker.patch(
        "fapolicy_analyzer.ui.session_manager.SessionManager.save_edit_session",
        side_effect=IOError,
    )
    uut_autosave_enabled.on_next_system({"changesets": mock_changesets_state()})
    mockFunc.assert_called()


def test_force_cleanup_autosave_sessions(uut):
    # Create a number of tmp files
    listCreatedTmpFiles = []
    for i in range(5):
        timestamp = DT.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S_%f")
        strFilename = uut._SessionManager__tmpFileBasename + "_" + timestamp + ".json"
        fp = open(strFilename, "w")
        fp.write(strFilename)
        fp.close()
        listCreatedTmpFiles.append(strFilename)

    # Invoke the cleanup function
    uut._SessionManager__force_cleanup_autosave_sessions()

    # Verify that all created tmp files have been deleted.
    listRemainingTmpFiles = [f for f in listCreatedTmpFiles if os.path.isfile(f)]
    assert len(listRemainingTmpFiles) == 0


def test_cleanup(uut):
    # Currently the public wrapper for __force_cleanup_autosave_sessions()
    # Create a number of tmp files
    listCreatedTmpFiles = []
    for i in range(5):
        timestamp = DT.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S_%f")
        strFilename = uut._SessionManager__tmpFileBasename + "_" + timestamp + ".json"
        fp = open(strFilename, "w")
        fp.write(strFilename)
        fp.close()
        listCreatedTmpFiles.append(strFilename)

    # Invoke the cleanup function
    uut.cleanup()

    # Verify that all created tmp files have been deleted.
    listRemainingTmpFiles = [f for f in listCreatedTmpFiles if os.path.isfile(f)]
    assert len(listRemainingTmpFiles) == 0


def test_autosave_filecount(uut_autosave_enabled, tmp_path):
    uut_autosave_enabled.set_autosave_filecount(3)
    uut_autosave_enabled.set_autosave_filename(os.path.join(tmp_path, "foo.tmp"))
    # Verify the sessionManager's attribute can be set
    assert uut_autosave_enabled._SessionManager__iTmpFileCount == 3

    strSearchPattern = uut_autosave_enabled._SessionManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)

    for changeset in test_changesets:
        uut_autosave_enabled.on_next_system(
            {"changesets": mock_changesets_state([changeset])}
        )

    # Verify there are three temp files on the filesystem
    strSearchPattern = uut_autosave_enabled._SessionManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    assert len(listTmpFiles) == 2


def test_detect_previous_session_no_files(uut):
    # There should be no existing tmp session files
    strSearchPattern = uut._SessionManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    assert not len(listTmpFiles)

    # The uut's detection function should verify no files too
    assert not uut.detect_previous_session()


def test_detect_previous_session_files(uut_autosave_enabled):
    uut_autosave_enabled.on_next_system({"changesets": mock_changesets_state()})

    # Verify there temp files on the filesystem
    strSearchPattern = uut_autosave_enabled._SessionManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    assert len(listTmpFiles) > 0

    # The uut's detection function should verify the existence of tmp files
    assert uut_autosave_enabled.detect_previous_session()

    # Clean up
    uut_autosave_enabled.cleanup()
    listTmpFiles = glob.glob(strSearchPattern)
    assert len(listTmpFiles) == 0


def test_restore_previous_session(uut_autosave_enabled, autosaved_files, mock_dispatch):
    # Two json files assumed on disk w/fixture
    strSearchPattern = uut_autosave_enabled._SessionManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    assert len(listTmpFiles) > 0

    # Convert to sets so that ordering is irrelevant
    assert set(listTmpFiles) == set(autosaved_files)
    assert uut_autosave_enabled.restore_previous_session()
    mock_dispatch.assert_called_with(Attr(type=APPLY_CHANGESETS))

    # verify changesets
    expected = test_changes
    # parse changesets to json string to compare
    args, _ = mock_dispatch.call_args
    actual = [
        {path: action for path, action in c.serialize().items()}
        if isinstance(c, TrustChangeset)
        else c.serialize()
        for c in args[0].payload
    ]

    assert actual == expected


def test_restore_previous_session_w_exception(
    uut_autosave_enabled, autosaved_files, mock_dispatch, mocker
):
    # Mock the open_edit_session() call such that it throws an exception
    mockFunc = mocker.patch(
        "fapolicy_analyzer.ui.session_manager.SessionManager.open_edit_session",
        side_effect=IOError,
    )

    # Two json files assumed on disk w/fixture
    strSearchPattern = uut_autosave_enabled._SessionManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    assert len(listTmpFiles) > 0

    # Convert to sets so that ordering is irrelevant
    assert set(listTmpFiles) == set(autosaved_files)
    assert not uut_autosave_enabled.restore_previous_session()
    mockFunc.assert_called()
    mock_dispatch.assert_not_called()
