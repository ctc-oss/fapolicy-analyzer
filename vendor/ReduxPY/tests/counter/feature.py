""" Exposes the feature creator """
from redux import ReduxFeatureModule, create_feature_module, select_feature, select

from .constants import FEATURE_NAME
from .reducer import COUNTER_REDUCER

select_counter_feature = select_feature(FEATURE_NAME)


def create_counter_feature() -> ReduxFeatureModule:
    """Creates a new feature module

    Returns:
        ReduxFeatureModule -- the feature module
    """
    return create_feature_module(FEATURE_NAME, COUNTER_REDUCER)
