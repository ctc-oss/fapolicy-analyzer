""" Exposes the feature creator """
from redux import ReduxFeatureModule, create_feature_module, select, select_feature

from .constants import FEATURE_NAME
from .reducer import todo_reducer

select_todos_feature = select_feature(FEATURE_NAME)


def create_todos_feature() -> ReduxFeatureModule:
    """Creates a new feature module

    Returns:
        ReduxFeatureModule -- the feature module
    """
    return create_feature_module(FEATURE_NAME, todo_reducer)
