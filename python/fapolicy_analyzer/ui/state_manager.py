#!/usr/bin/python3
# state_manager.py - A singleton wrapper class for maintaining global app state
# TPArchambault 2021.04.16
#
"""
A singleton wrapper class for maintaining global app state

Currently only maintains the Changeset FIFO queue

>>> from state_manager import StateManager
>>> sm=StateManager()
>>> sm.isDirtyQueue()
False
>>> sm.addChangeSetQ(1)
>>> sm.isDirtyQueue()
True
>>> sm.addChangeSetQ(1)
>>> sm.getChangeSetQ()
[1, 1]
>>> sm.delChangeSetQ()
False
>>> sm.isDirtyQueue()
False
>>> sm.getChangeSetQ()
[]
>>> sm.addChangeSetQ(1)
>>> sm.addChangeSetQ(2)
>>> sm.addChangeSetQ(3)
>>> sm.addChangeSetQ(4)
>>> sm.getChangeSetQ()
[1, 2, 3, 4]
>>> sm.nextChangeSetQ()
1
>>> sm.nextChangeSetQ()
2
>>> sm.getChangeSetQ()
[3, 4]
>>> sm.dumpState()
([3, 4], [])
>>> sm.redoChangeSetQ()
[3, 4]
>>> sm.dumpState()
([3, 4], [])
>>> sm.addChangeSetQ(10)
>>> sm.getChangeSetQ()
[3, 4, 10]
>>> sm.undoChangeSetQ()
[3, 4]
>>> sm.dumpState()
([3, 4], [10])
>>> sm.redoChangeSetQ()
[3, 4, 10]
>>> sm.dumpState()
([3, 4, 10], [])
>>> sm.nextChangeSetQ()
3
>>> sm.nextChangeSetQ()
4
>>> sm.undoChangeSetQ()
[]
>>> sm.dumpState()
([], [10])
>>> sm.redoChangeSetQ()
[10]
>>> sm.dumpState()
([10], [])
>>> sm.isDirtyQueue()
True
>>> sm.undoChangeSetQ()
[]
>>> sm.dumpState()
([], [10])
>>> sm.isDirtyQueue()
False
"""

from .configs import StateEvents

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
            self.listNotifyObjs.append(notify_list);

    def addChangeSetQ(self, change_set):
        """Add the change_set argument to the end of the FIFO queue"""
        self.listChangeset.append(change_set)
        self.updateDirtyQueue()

    def nextChangeSetQ(self):
        """Remove the next change_set from the front of the FIFO queue"""
        retChangeSet = self.listChangeset.pop(0)
        self.updateDirtyQueue()
        return retChangeSet

    def delChangeSetQ(self):
        """Delete the current Changeset FIFO queue"""
        self.listChangeset.clear()
        return self.updateDirtyQueue()

    def getChangeSetQ(self):
        """Returns the current change_set"""
        return self.listChangeset

    def dumpState(self):
        """Returns the current complete state of the StateManager instance."""
        return (self.listChangeset, self.listUndoChangeset)

    def undoChangeSetQ(self):
        """Removes the last change_set from the back of the queue"""
        if len(self.listChangeset) != 0:
            csTemp = self.listChangeset.pop()
            self.listUndoChangeset.append(csTemp);
            self.updateDirtyQueue()
        return self.getChangeSetQ()

    def redoChangeSetQ(self):
        """Adds previously undone changes back into the FIFO queue"""
        if len(self.listUndoChangeset) != 0:
            csTemp = self.listUndoChangeset.pop();
            self.listChangeset.append(csTemp)
            self.updateDirtyQueue()
        return self.getChangeSetQ()

    def addNotificationObj(self, objNotify):
        """Add an object to the end of the notification list"""
        self.listNotifyObjs.append(objNotify)

    def invokeNotifications(self, event_type):
        """Iterates through the notification list invoking state_event()
        on each object"""
        
        for o in self.listNotifyObjs:
            o.state_event(event_type)

    def isDirtyQueue(self):
        if len(self.listChangeset) != 0:
            return True
        return False
    
    def updateDirtyQueue(self):
        """Check that DirtyQueue member variable reflects status of changeset
        queue. If variable is not consistent, update and notify subscribers.
        Returns True is there are unapplied changes, False otherwise."""
        if self.bDirtyQ != self.isDirtyQueue():
            self.bDirtyQ = self.isDirtyQueue()
            if self.bDirtyQ:
                self.invokeNotifications(StateEvents.STATE_UNAPPLIED_CHANGES)
            else:
                self.invokeNotifications(StateEvents.STATE_UNAPPLIED_NONE)
        return self.bDirtyQ
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
