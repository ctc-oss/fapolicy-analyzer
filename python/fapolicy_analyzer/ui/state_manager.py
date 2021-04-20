#!/usr/bin/python3
# state_manager.py - A singleton wrapper class for maintaining global app state
# TPArchambault 2021.04.16
#
"""
A singleton wrapper class for maintaining global app state

Currently only maintains the Changeset FIFO queue

>>> from state_manager import StateManager
>>> sm=StateManager()
>>> sm.is_dirty_queue()
False
>>> sm.add_changeset_q(1)
>>> sm.is_dirty_queue()
True
>>> sm.add_changeset_q(1)
>>> sm.get_changeset_q()
[1, 1]
>>> sm.del_changeset_q()
False
>>> sm.is_dirty_queue()
False
>>> sm.get_changeset_q()
[]
>>> sm.add_changeset_q(1)
>>> sm.add_changeset_q(2)
>>> sm.add_changeset_q(3)
>>> sm.add_changeset_q(4)
>>> sm.get_changeset_q()
[1, 2, 3, 4]
>>> sm.next_changeset_q()
1
>>> sm.next_changeset_q()
2
>>> sm.get_changeset_q()
[3, 4]
>>> sm.dump_state()
([3, 4], [])
>>> sm.redo_changeset_q()
[3, 4]
>>> sm.dump_state()
([3, 4], [])
>>> sm.add_changeset_q(10)
>>> sm.get_changeset_q()
[3, 4, 10]
>>> sm.undo_changeset_q()
[3, 4]
>>> sm.dump_state()
([3, 4], [10])
>>> sm.redo_changeset_q()
[3, 4, 10]
>>> sm.dump_state()
([3, 4, 10], [])
>>> sm.next_changeset_q()
3
>>> sm.next_changeset_q()
4
>>> sm.undo_changeset_q()
[]
>>> sm.dump_state()
([], [10])
>>> sm.redo_changeset_q()
[10]
>>> sm.dump_state()
([10], [])
>>> sm.is_dirty_queue()
True
>>> sm.undo_changeset_q()
[]
>>> sm.dump_state()
([], [10])
>>> sm.is_dirty_queue()
False
"""

from enum import Enum

class StateEvents(Enum):
    """enum used to indicate the changed state."""
    STATE_UNAPPLIED_NONE = 0
    STATE_UNAPPLIED_CHANGES = 1

class StateManager(object):
    """A singleton wrapper class for maintaining global app state and changesets
    - Changeset FIFO queue
    - Current working Changeset

    A notify object will have its state_event() callback invoked upon state
    changes occuring in the StateManager instance.
    """
    def __init__(self, notify_list=None):
        self.listNotifyObjs = []
        self.listChangeset = [] #FIFO queue
        self.listUndoChangeset = [] # Undo Stack
        self.bDirtyQ = False

        # Populate notification list
        if notify_list:
            self.listNotifyObjs.append(notify_list)

    def add_changeset_q(self, change_set):
        """Add the change_set argument to the end of the FIFO queue"""
        self.listChangeset.append(change_set)
        self.update_dirty_queue()

    def next_changeset_q(self):
        """Remove the next changeset from the front of the FIFO queue"""
        retChangeSet = self.listChangeset.pop(0)
        self.update_dirty_queue()
        return retChangeSet

    def del_changeset_q(self):
        """Delete the current Changeset FIFO queue"""
        self.listChangeset.clear()
        return self.update_dirty_queue()

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
            self.update_dirty_queue()
        return self.get_changeset_q()

    def redo_changeset_q(self):
        """Adds previously undone changes back into the FIFO queue"""
        if self.listUndoChangeset:
            csTemp = self.listUndoChangeset.pop()
            self.listChangeset.append(csTemp)
            self.update_dirty_queue()
        return self.get_changeset_q()

    def add_notification_obj(self, objNotify):
        """Add an object to the end of the notification list"""
        self.listNotifyObjs.append(objNotify)

    def invoke_notifications(self, event_type):
        """Iterates through the notification list invoking state_event()
        on each object"""
        for o in self.listNotifyObjs:
            o.state_event(event_type)

    def is_dirty_queue(self):
        """Returns True if the queue size is not zero, otherwise False"""
        if self.listChangeset:
            return True
        return False

    def update_dirty_queue(self):
        """Check that DirtyQueue member variable reflects status of changeset
        queue. If variable is not consistent, update and notify subscribers.
        Returns True is there are unapplied changes, False otherwise."""
        if self.bDirtyQ != self.is_dirty_queue():
            self.bDirtyQ = self.is_dirty_queue()
            if self.bDirtyQ:
                self.invoke_notifications(StateEvents.STATE_UNAPPLIED_CHANGES)
            else:
                self.invoke_notifications(StateEvents.STATE_UNAPPLIED_NONE)
        return self.bDirtyQ

if __name__ == "__main__":
    import doctest
    doctest.testmod()
