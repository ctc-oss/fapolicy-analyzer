from events import Events


class StateManager(Events):
    """A singleton wrapper class for maintaining global app state and changesets
    - Changeset FIFO queue
    - Current working Changeset

    A notify object will have its state_event() callback invoked upon state
    changes occuring in the StateManager instance.
    """

    __events__ = ["changeset_queue_updated"]

    def __init__(self):
        Events.__init__(self)
        self.listChangeset = []  # FIFO queue
        self.listUndoChangeset = []  # Undo Stack
        self.bDirtyQ = False

    def add_changeset_q(self, change_set):
        """Add the change_set argument to the end of the FIFO queue"""
        self.listChangeset.append(change_set)
        self.__update_dirty_queue()

    def next_changeset_q(self):
        """Remove the next changeset from the front of the FIFO queue"""
        retChangeSet = self.listChangeset.pop(0)
        self.__update_dirty_queue()
        return retChangeSet

    def del_changeset_q(self):
        """Delete the current Changeset FIFO queue"""
        self.listChangeset.clear()
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
            self.__update_dirty_queue()
        return self.get_changeset_q()

    def redo_changeset_q(self):
        """Adds previously undone changes back into the FIFO queue"""
        if self.listUndoChangeset:
            csTemp = self.listUndoChangeset.pop()
            self.listChangeset.append(csTemp)
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
            self.changeset_queue_updated()
        return self.bDirtyQ

    def get_path_action_list(self):
        listReturn = []

        # Iterate through the StateManagers Changeset list
        for e in self.listChangeset:

            # Each changeset contains a dict with at least one Path/Action pair
            #print(e.get_path_action_map())
            for t in e.get_path_action_map().items():
                listReturn.append(t)

        #print( listReturn)
        return listReturn
        #return [("Its the time ","of the season"),("when love", "run high...")]
        #return ["Now is ", "the time..."]
        

stateManager = StateManager()
