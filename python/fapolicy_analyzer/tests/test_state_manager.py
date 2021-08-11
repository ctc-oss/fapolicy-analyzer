import context  # noqa: F401
import os
import pytest
import json
import glob
from datetime import datetime as DT
import time
from unittest.mock import MagicMock
from fapolicy_analyzer import Changeset
from ui.state_manager import StateManager, NotificationType


# Set up; create UUT
@pytest.fixture
def uut():
    stateManager = StateManager()
    stateManager.set_autosave_enable(False)
    stateManager.set_autosave_filename("/tmp/UnitTestSession")
    yield stateManager
    stateManager.cleanup()
    stateManager = None


@pytest.fixture
def populated_queue(uut):
    # Fill it up
    uut.add_changeset_q(1)
    uut.add_changeset_q(2)
    uut.add_changeset_q(3)
    uut.add_changeset_q(4)
    return uut


@pytest.fixture
def uut_autosave_enabled():
    stateManager = StateManager()
    stateManager.set_autosave_enable(True)
    yield stateManager
    stateManager.cleanup()
    stateManager = None


@pytest.fixture
def populated_changeset_list():
    listExpectedChangeset = []
    for i in range(4):
        changeset = Changeset()
        strFilename = "/tmp/filename{}.txt".format(i)

        # Alternate Adds/Deletes for testing coverage
        if i % 2 == 0:
            # Even counts
            changeset.add_trust(strFilename)
        else:
            # Odd counts
            changeset.del_trust(strFilename)
        listExpectedChangeset.append(changeset)

    yield listExpectedChangeset


@pytest.fixture
def autosaved_files():
    fp0 = open("/tmp/FaCurrentSession.tmp_20210803_130622_059045.json", "w")
    fp1 = open("/tmp/FaCurrentSession.tmp_20210803_130622_065690.json", "w")
    fp0.write('''{
    "/home/toma/Development/CTC/data_space/man_from_mars.txt": "Add",
    "/home/toma/Integration.json": "Add"
}''')
    fp1.write('''{
    "/home/toma/Development/CTC/data_space/man_from_mars.txt": "Add",
    "/home/toma/Development/CTC/data_space/this/is/a/longer/path/now_is_the_time.txt": "Del",
    "/home/toma/Integration.json": "Add"
}''')
    fp0.close()
    fp1.close()

    # yields the newest json file.
    yield ["/tmp/FaCurrentSession.tmp_20210803_130622_065690.json",
           "/tmp/FaCurrentSession.tmp_20210803_130622_059045.json"]

    # Clean up the filesystem
    os.remove("/tmp/FaCurrentSession.tmp_20210803_130622_059045.json")
    os.remove("/tmp/FaCurrentSession.tmp_20210803_130622_065690.json")


@pytest.fixture
def autosaved_w_bad_file():
    fp0 = open("/tmp/FaCurrentSession.tmp_20210803_130622_059045.json", "w")
    fp1 = open("/tmp/FaCurrentSession.tmp_20210803_130622_065690.json", "w")
    fp0.write('''{
    "/home/toma/Development/CTC/data_space/man_from_mars.txt": "Add",
    "/home/toma/Integration.json": "Add"
}''')
    fp1.write('''{
    "/home/toma/Development/CTC/data_space/man_from_mars.txt": "Add",
    "/home/toma/Development/CTC/data_space/this/is/a/longer/path/now_is_the_time.txt": "Del",
    "/home/toma/Integration.json": "Add"
''')
    fp0.close()
    fp1.close()

    # yields the newest json file.
    yield ["/tmp/FaCurrentSession.tmp_20210803_130622_065690.json",
           "/tmp/FaCurrentSession.tmp_20210803_130622_059045.json"]

    # Clean up the filesystem
    os.remove("/tmp/FaCurrentSession.tmp_20210803_130622_059045.json")
    os.remove("/tmp/FaCurrentSession.tmp_20210803_130622_065690.json")


def test_add_empty_queue(uut):
    """
    test: add an element to an empty Q, verify Q contents
    """
    # Verify empty Q
    assert not uut.is_dirty_queue()

    # Test adding to an empty queue
    uut.add_changeset_q(10)
    assert uut.is_dirty_queue()

    # Verify Q contents
    assert uut.get_changeset_q() == [10]


# test: add an element to a populated Q, verify Q contents
def test_add_populated_queue(populated_queue):
    # Verify populated Q
    assert populated_queue.get_changeset_q() == [1, 2, 3, 4]
    assert populated_queue.is_dirty_queue()

    # Test adding to an populated queue
    populated_queue.add_changeset_q(5)
    assert populated_queue.is_dirty_queue()

    # Verify Q contents
    assert populated_queue.get_changeset_q() == [1, 2, 3, 4, 5]


# test: Delete the contents of a populated Q, verify pre/post Q contents
def test_del_populated_queue(populated_queue):
    # Verify populated Q contents
    assert populated_queue.get_changeset_q() == [1, 2, 3, 4]

    # Delete contents of the populated queue
    populated_queue.del_changeset_q()
    assert not populated_queue.is_dirty_queue()
    assert populated_queue.get_changeset_q() == []


# test: Get the next element out of a FIFO Q, verify pre/post Q contents
def test_next_populated_queue(populated_queue):
    # Verify populated Q contents
    assert populated_queue.get_changeset_q() == [1, 2, 3, 4]

    # Delete contents of the populated queue
    assert populated_queue.next_changeset_q() == 1
    assert populated_queue.next_changeset_q() == 2
    assert populated_queue.is_dirty_queue()
    assert populated_queue.get_changeset_q() == [3, 4]


# test: Verify dump_state() functionality
def test_dump_state(populated_queue):
    # Verify stateManager state after two next ops.
    assert populated_queue.next_changeset_q() == 1
    assert populated_queue.next_changeset_q() == 2
    assert populated_queue.dump_state() == ([3, 4], [])


# test: Verify undo/redo functionality
def test_undo_redo_queue(populated_queue):
    # Verify stateManager state after two next ops.
    assert populated_queue.next_changeset_q() == 1
    assert populated_queue.next_changeset_q() == 2
    populated_queue.add_changeset_q(10)
    assert populated_queue.dump_state() == ([3, 4, 10], [])

    # Redo with the undo Q empty
    populated_queue.redo_changeset_q()
    assert populated_queue.dump_state() == ([3, 4, 10], [])

    # Undo with the undo Q empty
    populated_queue.undo_changeset_q()
    assert populated_queue.dump_state() == ([3, 4], [10])

    # Redo with a populated undo Q
    populated_queue.redo_changeset_q()
    assert populated_queue.dump_state() == ([3, 4, 10], [])


# test: Verify is_dirty_queue() when Q shifts from empty to populated to empty
def test_is_dirty_queue(uut):
    # Verify empty
    assert not uut.is_dirty_queue()
    uut.add_changeset_q(1)
    assert uut.is_dirty_queue()
    uut.add_changeset_q(2)
    assert uut.is_dirty_queue()
    assert uut.next_changeset_q() == 1
    assert uut.next_changeset_q() == 2
    assert not uut.is_dirty_queue()


@pytest.mark.parametrize("notification_type", list(NotificationType))
def test_system_notification_added(uut, notification_type):
    mock = MagicMock()
    uut.system_notification_added += mock
    uut.add_system_notification("foo", notification_type)
    mock.assert_called_with(("foo", notification_type))
    uut.system_notification_added -= mock


@pytest.mark.parametrize("notification_type", list(NotificationType))
def test_system_notification_removed(uut, notification_type):
    mock = MagicMock()
    uut.system_notification_removed += mock
    uut.add_system_notification("foo", notification_type)
    uut.remove_system_notification()
    mock.assert_called_with(("foo", notification_type))
    uut.system_notification_removed -= mock


# ######################## Session Serialization #####################
def test_open_edit_session(uut, mocker):
    """Tests StateManager's open json session file load functionality.
    The tested function 'open_edit_session()' converts a json file of
    paths and associated actions, and converts that into a list of
    Path/Action tuple pairs, then communicates with the AncillaryTrust
    DatabaseAdmin's (ATDA) via an event.

    Test approach:
    1. A reference json file is generated and wrote to disk.
    2. The StateManager's load/open function is invoked to read and parse
    the reference file.
    3. The Event channel call and associated argument is verified and compared to the
    expected argument.

 - Mocking: The Event channel function in the _EventSlot class that will
    send a list of Path/Action tuples.
"""
    mockEvent = mocker.patch("events.events._EventSlot.__call__")
    # Create Path/Action dict and expected generated path/action tuple list.
    dictPaInput = {
        "/data_space/man_from_mars.txt": "Add",
        "/data_space/this/is/a/longer/path/now_is_the_time.txt": "Del",
        "/data_space/Integration.json": "Add"
    }

    listPaTuplesExpected = [
        ('/data_space/Integration.json', 'Add'),
        ('/data_space/man_from_mars.txt', 'Add'),
        ('/data_space/this/is/a/longer/path/now_is_the_time.txt', 'Del')
    ]

    # Directly generate reference test json input file
    tmp_file = "/tmp/FaPolicyAnalyzerTest.tmp"
    with open(tmp_file, "w") as fpJson:
        json.dump(dictPaInput, fpJson, sort_keys=True, indent=4)

    # Process the json reference file via fapolicy-analyzer's datapath
    uut.open_edit_session(tmp_file)

    # Clean up of the json reference file
    os.system("rm -f {}".format(tmp_file))

    # Verify the event channel function was called w/appropriate args
    mockEvent.assert_called_with(listPaTuplesExpected)


def test_open_edit_session_w_exception(uut, mocker):
    """Tests StateManager's open json session file load functionality.
    The tested function 'open_edit_session()' converts a json file of
    paths and associated actions, and converts that into a list of
    Path/Action tuple pairs, then communicates with the AncillaryTrust
    DatabaseAdmin's (ATDA) via an event.

    Test approach:
    1. A reference json file is generated and wrote to disk.
    2. The StateManager's load/open function is invoked to read and parse
    the reference file.
    3. The Event channel call and associated argument is verified and compared to the
    expected argument.

 - Mocking: The json.load() function will generate an exception.
"""
    mockFunc = mocker.patch("ui.state_manager.json.load",
                            side_effect=IOError)

    # Create Path/Action dict and expected generated path/action tuple list.
    dictPaInput = {
        "/data_space/man_from_mars.txt": "Add",
        "/data_space/this/is/a/longer/path/now_is_the_time.txt": "Del",
        "/data_space/Integration.json": "Add"
    }

    # Directly generate reference test json input file
    tmp_file = "/tmp/FaPolicyAnalyzerTest.tmp"
    with open(tmp_file, "w") as fpJson:
        json.dump(dictPaInput, fpJson, sort_keys=True, indent=4)

    # Process the json reference file via fapolicy-analyzer's datapath
    uut.open_edit_session(tmp_file)

    # Clean up of the json reference file
    os.system("rm -f {}".format(tmp_file))

    # Verify the event channel function was called w/appropriate args
    mockFunc.assert_called()


def test_save_edit_session(uut):
    """Tests StateManager's save json session file functionality.
    The tested function 'save_edit_session()' converts the embedded Changeset
    queue into a a list of Path/Action tuple pairs, then a dict, which dumps
    via the json module into a json file of paths and associated actions.

    Test approach:
    1. The StateManager's internal queue is populated with Path/Action data
    leveraging the utility function: __path_action_list_2_queue()
    2. The StateManager function is invoked to write the contents of the queue
    (which is the current edit session's undeployed operations) to a json
    file.
    3. Independently create json objects from the output file and from a
    json text string. Compare those objects.
    the reference file.
    3. The calls and arguments to the AncillaryTrustDatabaseAdmin's (ATDA)
    on_files_added() and on_files_deleted() are verified and compared to the
    expected arguments.

    ToDo: Research if json is the appropriate format for maintaining
    session operation ordering which may/may not matter if flattened.
"""

    # Define reference json text and generated filename
    tmp_file_out = "/tmp/FaPolicyAnalyzerUnitTestOutput.tmp.json"

    jsonText = '''{
    "/data_space/man_from_mars.txt": "Add",
    "/data_space/this/is/a/longer/path/now_is_the_time.txt": "Del",
    "/data_space/Integration.json": "Add"
}
'''

    # Populate the StateManager's Queue w/equivalent data, write json file
    listPaTuples = [
        ("/data_space/man_from_mars.txt", "Add"),
        ("/data_space/this/is/a/longer/path/now_is_the_time.txt", "Del"),
        ("/data_space/Integration.json", "Add")]

    uut._StateManager__path_action_list_2_queue(listPaTuples)
    uut.save_edit_session(tmp_file_out)

    # Independently create json objects from the output file and from the
    # json text string above. Compare the reference object
    # w/the object created from the json file.
    with open(tmp_file_out) as fpJson:
        strJsonReference = json.dumps(json.loads(jsonText), sort_keys=True)
        strJsonGeneratedFile = json.dumps(json.load(fpJson), sort_keys=True)
        assert strJsonReference == strJsonGeneratedFile

    # Clean up tmp file
    os.system("rm -f {}".format(tmp_file_out))


# ########################### Autosave Sessions #################
def test_autosave_edit_session(uut_autosave_enabled,
                               populated_changeset_list
                               ):
    for cs in populated_changeset_list:
        uut_autosave_enabled.add_changeset_q(cs)

    # Get the StateManager's changeset Q and compare it to the original list
    assert populated_changeset_list == uut_autosave_enabled.get_changeset_q()


def test_autosave_edit_session_w_exception(mocker, uut_autosave_enabled):
    # Create a mock that throw an exception side-effect
    mockFunc = mocker.patch("ui.state_manager.StateManager.save_edit_session",
                            side_effect=IOError)

    # Populate a single Changeset and add it to the StateManager's queue
    cs = Changeset()
    strFilename = "/tmp/DeadBeef.txt"
    cs.add_trust(strFilename)
    uut_autosave_enabled.add_changeset_q(cs)
    mockFunc.assert_called()


def test_force_cleanup_autosave_sessions(uut):
    # Create a number of tmp files
    listCreatedTmpFiles = []
    for i in range(5):
        timestamp = DT.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S_%f')
        strFilename = uut._StateManager__tmpFileBasename + "_" + timestamp + ".json"
        fp = open(strFilename, "w")
        fp.write(strFilename)
        fp.close()
        listCreatedTmpFiles.append(strFilename)

    # Invoke the cleanup function
    uut._StateManager__force_cleanup_autosave_sessions()

    # Verify that all created tmp files have been deleted.
    listRemainingTmpFiles = []
    for f in listCreatedTmpFiles:
        if os.path.isfile(f):
            listRemainingTmpFiles.append(f)
    assert len(listRemainingTmpFiles) == 0


def test_cleanup(uut):
    # Currently the public wrapper for __force_cleanup_autosave_sessions()
    # Create a number of tmp files
    listCreatedTmpFiles = []
    for i in range(5):
        timestamp = DT.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S_%f')
        strFilename = uut._StateManager__tmpFileBasename + "_" + timestamp + ".json"
        fp = open(strFilename, "w")
        fp.write(strFilename)
        fp.close()
        listCreatedTmpFiles.append(strFilename)

    # Invoke the cleanup function
    uut.cleanup()

    # Verify that all created tmp files have been deleted.
    listRemainingTmpFiles = []
    for f in listCreatedTmpFiles:
        if os.path.isfile(f):
            listRemainingTmpFiles.append(f)
    assert len(listRemainingTmpFiles) == 0


def test_autosave_filecount(uut_autosave_enabled,
                            populated_changeset_list
                            ):
    # Verify the StateManager's attribute can be set
    uut_autosave_enabled.set_autosave_filecount(3)
    assert uut_autosave_enabled._StateManager__iTmpFileCount == 3

    for cs in populated_changeset_list:
        uut_autosave_enabled.add_changeset_q(cs)

    # Verify there are three temp files on the filesystem
    strSearchPattern = uut_autosave_enabled._StateManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    assert len(listTmpFiles) == 3


def test_detect_previous_session_no_files(uut):
    # There should be no existing tmp session files
    strSearchPattern = uut._StateManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    assert not len(listTmpFiles)

    # The uut's detection function should verify no files too
    assert not uut.detect_previous_session()


def test_detect_previous_session_files(uut_autosave_enabled,
                                       populated_changeset_list):
    # Apply a number of Changesets which each generate a tmp session file
    for cs in populated_changeset_list:
        uut_autosave_enabled.add_changeset_q(cs)

    # Verify there temp files on the filesystem
    strSearchPattern = uut_autosave_enabled._StateManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    assert len(listTmpFiles) > 0

    # The uut's detection function should verify the existence of tmp files
    assert uut_autosave_enabled.detect_previous_session()

    # Clean up
    uut_autosave_enabled.cleanup()
    listTmpFiles = glob.glob(strSearchPattern)
    assert len(listTmpFiles) == 0


def test_restore_previous_session(uut_autosave_enabled,
                                  populated_changeset_list,
                                  autosaved_files,
                                  mocker):

    # Mock the event channel comms to the ATDA
    # mockEvent = mocker.patch("ui.state_manager.ev_user_session_loader")

    # Two json files assumed on disk w/fixture
    strSearchPattern = uut_autosave_enabled._StateManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    print(strSearchPattern, listTmpFiles)
    assert len(listTmpFiles) > 0

    # Convert to sets so that ordering is irrelevant
    assert set(listTmpFiles) == set(autosaved_files)
    assert uut_autosave_enabled.restore_previous_session()


def test_restore_previous_session_w_exception(uut_autosave_enabled,
                                              autosaved_files,
                                              mocker):
    # Mock the open_edit_session() call such that it throws an exception
    mockFunc = mocker.patch("ui.state_manager.StateManager.open_edit_session",
                            side_effect=IOError)

    # Two json files assumed on disk w/fixture
    strSearchPattern = uut_autosave_enabled._StateManager__tmpFileBasename + "_*.json"
    listTmpFiles = glob.glob(strSearchPattern)
    print(strSearchPattern, listTmpFiles)
    assert len(listTmpFiles) > 0

    # Convert to sets so that ordering is irrelevant
    assert set(listTmpFiles) == set(autosaved_files)
    assert not uut_autosave_enabled.restore_previous_session()
    mockFunc.assert_called()


def test_restore_previous_session_w_bad_file(uut_autosave_enabled,
                                             autosaved_w_bad_file,
                                             mocker):
    # Write two json files to disk, the second with bad json syntax.
    assert 1


# ##################### Queue mgmt utilities #########################
def test_path_action_dict_to_list(uut):
    # Define test input/output data
    dictPA = {"/data_space/man_from_mars.txt": "Add",
              "/data_space/this/is/a/longer/path/now_is_the_time.txt": "Del",
              "/data_space/Integration.json": "Add"}

    listPaExpected = [
        ("/data_space/man_from_mars.txt", "Add"),
        ("/data_space/this/is/a/longer/path/now_is_the_time.txt", "Del"),
        ("/data_space/Integration.json", "Add")]

    listPaTuplesGenerated = uut._StateManager__path_action_dict_to_list(dictPA)
    assert listPaTuplesGenerated == listPaExpected


def test_path_action_list_2_queue(uut):
    """Test: The utility function, __path_action_list_2_queue() loads the
    internal queue with test data. The contents of the queue is then dumped
    using  another utility, get_path_action_list(). Those input and output
    data lists are then compared.
"""
    listPaTuples = [
        ("/data_space/man_from_mars.txt", "Add"),
        ("/data_space/this/is/a/longer/path/now_is_the_time.txt", "Del"),
        ("/data_space/Integration.json", "Add")]

    assert not uut.is_dirty_queue()
    uut._StateManager__path_action_list_2_queue(listPaTuples)
    assert uut.is_dirty_queue()
    listQueueContents = uut.get_path_action_list()
    assert listPaTuples == listQueueContents


def test_path_action_list_2_queue_w_bad_data(uut):
    listPaTuples = [
        ("/data_space/man_from_mars.txt", "Add"),
        ("/data_space/this/is/a/longer/path/now_is_the_time.txt", "Del"),
        ("/data_space/Integration.json", "BAD")]

    listPaExpected = [
        ("/data_space/man_from_mars.txt", "Add"),
        ("/data_space/this/is/a/longer/path/now_is_the_time.txt", "Del")]

    assert not uut.is_dirty_queue()
    uut._StateManager__path_action_list_2_queue(listPaTuples)
    assert uut.is_dirty_queue()
    listQueueContents = uut.get_path_action_list()
    assert listPaExpected == listQueueContents


def test_path_action_list_to_dict(uut):
    listPaTuples = [
        ("/data_space/man_from_mars.txt", "Add"),
        ("/data_space/this/is/a/longer/path/now_is_the_time.txt", "Del"),
        ("/data_space/Integration.json", "Add")]

    dictPaExpected = {
        "/data_space/man_from_mars.txt": "Add",
        "/data_space/this/is/a/longer/path/now_is_the_time.txt": "Del",
        "/data_space/Integration.json": "Add"
    }

    uut._StateManager__path_action_list_2_queue(listPaTuples)
    dictPaCurrentQ = uut._StateManager__path_action_list_to_dict()
    assert dictPaExpected == dictPaCurrentQ
