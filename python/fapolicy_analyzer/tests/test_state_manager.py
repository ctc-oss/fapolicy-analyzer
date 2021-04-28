# test_state_manager.py
"""The embedded Changeset queue is tested with integers although any
 object type can be an element."""

import pytest
from ui.state_manager import stateManager

# Set up; create UUT
@pytest.fixture
def uut():
    # Return existing singleton
    stateManager.del_changeset_q()
    return stateManager

@pytest.fixture
def populated_queue(uut):
    # Fill it up
    uut.del_changeset_q()
    uut.add_changeset_q(1)
    uut.add_changeset_q(2)
    uut.add_changeset_q(3)
    uut.add_changeset_q(4)
    return uut
    
# test: add an element to an empty Q, verify Q contents
def test_add_empty_queue(uut):
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
    print(populated_queue)
    assert populated_queue.get_changeset_q() == [1,2,3,4]
    assert populated_queue.is_dirty_queue()
    
    # Test adding to an populated queue
    populated_queue.add_changeset_q(5)
    assert populated_queue.is_dirty_queue()

    # Verify Q contents
    assert populated_queue.get_changeset_q() == [1,2,3,4,5]

# test: Delete the contents of a populated Q, verify pre/post Q contents
def test_del_populated_queue(populated_queue):
    # Verify populated Q contents
    assert populated_queue.get_changeset_q() == [1,2,3,4]
    
    # Delete contents of the populated queue
    populated_queue.del_changeset_q()
    assert not populated_queue.is_dirty_queue()
    assert populated_queue.get_changeset_q() == []

# test: Get the next element out of a FIFO Q, verify pre/post Q contents
def test_next_populated_queue(populated_queue):
    # Verify populated Q contents
    assert populated_queue.get_changeset_q() == [1,2,3,4]
    
    # Delete contents of the populated queue
    assert populated_queue.next_changeset_q() == 1
    assert populated_queue.next_changeset_q() == 2
    assert populated_queue.is_dirty_queue()
    assert populated_queue.get_changeset_q() == [3,4]

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
