""" Action objects and constants """
from redux import create_action
from .constants import FEATURE_NAME


ACTION_INCREMENT = '%s Increment' % FEATURE_NAME
ACTION_DECREMENT = '%s Decrement' % FEATURE_NAME

DECREMENT_ACTION = create_action(ACTION_DECREMENT)(1)
INCREMENT_ACTION = create_action(ACTION_INCREMENT)(1)
