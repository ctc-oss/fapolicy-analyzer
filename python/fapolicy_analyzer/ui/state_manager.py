import logging
from enum import Enum
from events import Events
from fapolicy_analyzer import Changeset, System
from os import path
from collections import OrderedDict
from datetime import datetime as DT
import atexit
import os
import glob
import time
import json

class NotificationType(Enum):
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    SUCCESS = "success"


class StateManager(Events):
    """A singleton wrapper class for maintaining global app state and changesets
    - Changeset FIFO queue
    - Current working Changesets
    - Edit session tmp file management (default location is under /tmp which
      is assumed to be persistent between reboots

    A notify object will have its state_event() callback invoked upon state
    changes occuring in the StateManager instance.
    """

    __events__ = [
        "ev_changeset_queue_updated",
        "system_notification_added",
        "system_notification_removed",
        "ev_user_session_loaded"
    ]

    def __init__(self,
                 tmpFileBasename="/tmp/FaCurrentSession.tmp",
                 iTmpFileCount=2):
        Events.__init__(self)
        self.system = System()
        self.listChangeset = []  # FIFO queue
        self.listUndoChangeset = []  # Undo Stack
        self.bDirtyQ = False
        self.systemNotification = None
        self.__tmpFileBasename = tmpFileBasename
        self.__listAutosavedFilenames = []
        self.__iTmpFileCount = iTmpFileCount

        # Register cleanup callback function
        atexit.register(self.cleanup)
        
    def cleanup(self):
        """StateManager singleton / global object clean-up
effectively the StateManager's destructor."""
        logging.debug("StateManager::cleanup()")
        self.__force_cleanup_autosave_sessions()

    ######################## Changeset Queue ############################## 
    def add_changeset_q(self, change_set):
        """Add the change_set argument to the end of the FIFO queue"""
        self.listChangeset.append(change_set)
        self.autosave_edit_session()
        self.__update_dirty_queue()

    def next_changeset_q(self):
        """Remove the next changeset from the front of the FIFO queue"""
        retChangeSet = self.listChangeset.pop(0)
        self.autosave_edit_session()
        self.__update_dirty_queue()
        return retChangeSet

    def del_changeset_q(self):
        """Delete the current Changeset FIFO queue"""
        self.listChangeset.clear()
        # Remove tmp files
        self.__cleanup_autosave_sessions()
        return self.__update_dirty_queue()

    def get_changeset_q(self):
        """Returns the current change_set"""
        return self.listChangeset

    def dump_state(self):
        """Returns the current complete state of the StateManager instance."""
        return (self.listChangeset, self.listUndoChangeset)

    def undo_changeset_q(self):
        """Removes the last changeset from the back of the queue"""
        if self.listChangeset:
            csTemp = self.listChangeset.pop()
            self.listUndoChangeset.append(csTemp)
            self.autosave_edit_session()
            self.__update_dirty_queue()
        return self.get_changeset_q()

    def redo_changeset_q(self):
        """Adds previously undone changes back into the FIFO queue"""
        if self.listUndoChangeset:
            csTemp = self.listUndoChangeset.pop()
            self.listChangeset.append(csTemp)
            self.autosave_edit_session()
            self.__update_dirty_queue()
        return self.get_changeset_q()

    def is_dirty_queue(self):
        """Returns True if the queue size is not zero, otherwise False"""
        if self.listChangeset:
            return True
        return False

    def __update_dirty_queue(self):
        """Check that DirtyQueue member variable reflects status of changeset
        queue. If variable is not consistent, update and notify subscribers.
        Returns True is there are unapplied changes, False otherwise."""
        if self.bDirtyQ != self.is_dirty_queue():
            self.bDirtyQ = self.is_dirty_queue()
            self.ev_changeset_queue_updated()
        return self.bDirtyQ

    # ##################### Queue conversion utilities #####################
    def get_path_action_list(self):
        # Iterate through the StateManagers Changeset list
        # Each changeset contains a dict with at least one Path/Action pair
        # The rationale for the tuple format is the Gtk TreeView widget display
        return [t for e in self.listChangeset for t in e.get_path_action_map().items()]

    def __path_action_list_2_queue(self, listPathAction):
        """Converts a list of Path/Action tuples to populate changeset queue
This is a utility function intended for unit testing and troubleshooting
the StateManager and its interactions with interfacing objects. It is used to
populate the internal queue structure with Changeset objects, however it does
not exercise the full normal end to end data path which will normally apply and
deploy these changesets.
"""
        for e in listPathAction:
            cs = Changeset()
            if e[1] == "Add":
                cs.add_trust(e[0])
            elif e[1] == "Del":
                cs.del_trust(e[0])
            else:
                print("Error: Path/Action Pair: "
                      "Unknown Action: {} {}".format(e[0], e[1]))
                continue
            self.add_changeset_q(cs)

    def __path_action_list_to_dict(self):
        """Convert Path/Action list of tuple pairs to dict for json xfer"""
        dictPA = dict()
        for t in self.get_path_action_list():
            dictPA[t[0]] = t[1]
        logging.debug("Path/Action Dict: {}".format(dictPA))
        return dictPA

    def __path_action_dict_to_list(self, dictPathAction):
        """Convert Path/Action dict to list of tuple pairs for json xfer"""
        listPaTuples = list()
        for e in dictPathAction.keys():
            listPaTuples.append((e, dictPathAction[e]))
        logging.debug("PathAction Tuple List: {}".format(listPaTuples))
        return listPaTuples

    # ######################## Edit Session Mgmt ############################
    def save_edit_session(self, strJsonFile):
        """Save the pending changeset queue to the specified json file"""
        logging.debug("StateManager::save_edit_session({})".format(strJsonFile))
        with open(strJsonFile, "w") as fp:
            json.dump(self.__path_action_list_to_dict(), fp,
                      sort_keys=True,
                      indent=4)

    def open_edit_session(self, strJsonFile):
        """Save the FIFO changeset queue to the specified json file on disk"""
        logging.debug("Entered StateManager::open_edit_session({})"
                      .format(strJsonFile))
        listPA = None
        with open(strJsonFile, "r") as fp:
            d = json.load(fp, object_pairs_hook=OrderedDict)
            logging.debug("Loaded dict = ", d)
            listPA = self.__path_action_dict_to_list(d)
            logging.debug("StateManager::open_edit_session():{}".format(listPA))

            # Deleting current edit session history prior to replacing it.
            if listPA:
                # ToDo: Delete pending ops in the ATDA's embedded TreeView
                self.del_changeset_q()
            self.ev_user_session_loaded(listPA)

    ######################## Autosave file mgmt ###########################
    def __cleanup_autosave_sessions(self):
        """Deletes all current autosaved session files. These files were
created during the current editing session, and are deleted after a deploy,
or a session file open/restore operation."""
        logging.debug("StateManager::__cleanup_autosave_sessions()")
        print(self.__listAutosavedFilenames)
        for f in self.__listAutosavedFilenames:
            os.remove(f)
        self.__listAutosavedFilenames.clear()
        

    def __force_cleanup_autosave_sessions(self):
        """Brute force delete all detected autosave files"""
        logging.debug("StateManager::__force_cleanup_autosave_sessions()")
        strSearchPattern = self.__tmpFileBasename+"_*.json"
        print("Search Pattern: {}".format(strSearchPattern))
        listTmpFiles = glob.glob(strSearchPattern)
        logging.debug("Glob search results: {}".format(listTmpFiles))
        if listTmpFiles:
            for f in listTmpFiles:
                if os.path.isfile(f):
                    logging.debug("Session file detected: {}".format(f))
                    self.__listAutosavedFilenames.append(f)
            self.__cleanup_autosave_sessions()

    
    def autosave_edit_session(self):
        """Constructs a new tmp session filename w/timestamp, populates it with
 the current session state, saves it, and deletes the oldest tmp session file"""
        logging.debug("StateManager::autosave_edit_session()")
        timestamp = DT.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S_%f')
        strFilename = self.__tmpFileBasename+"_"+timestamp+".json"
        logging.debug("  Writing to: {}".format(strFilename))
        try:
            self.save_edit_session(strFilename)
            self.__listAutosavedFilenames.append(strFilename)
            logging.debug(self.__listAutosavedFilenames)
            
            # Delete oldest tmp file
            if (len(self.__listAutosavedFilenames) > self.__iTmpFileCount):
                self.__listAutosavedFilenames.sort().reverse()
                strOldestFile = self.__listAutosavedFilenames[0]
                logging.debug("Deleting: {}".format(strOldestFile))
                os.remove(strOldestFile)
                del(self.__listAutosavedFilenames[0])
                print(self.__listAutosavedFilenames)
                            
        except IOError as error:
            print("Warning: autosave_edit_session() failed: {}".format(error))
            print("Continuing...")

    ######################## Notification Events ##########################
    def add_system_notification(self,
                                notification: str,
                                notification_type: NotificationType):
        self.systemNotification = (notification, notification_type)
        self.system_notification_added(self.systemNotification)

    def remove_system_notification(self):
        self.system_notification_removed(self.systemNotification)
        self.systemNotification = None


stateManager = StateManager()
