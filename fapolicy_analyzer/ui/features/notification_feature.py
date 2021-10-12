from fapolicy_analyzer.ui.reducers import notification_reducer
from redux import create_feature_module, ReduxFeatureModule

NOTIFICATIONS_FEATURE = "notifications"


def create_notification_feature() -> ReduxFeatureModule:
    return create_feature_module(NOTIFICATIONS_FEATURE, notification_reducer)
