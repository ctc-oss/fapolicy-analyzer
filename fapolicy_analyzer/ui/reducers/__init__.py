from typing import Tuple
from .daemon_reducer import daemon_reducer
from .notification_reducer import notification_reducer
from .system_reducer import system_reducer

__all__: Tuple[str, ...] = ("notification_reducer",
                            "system_reducer",
                            "daemon_reducer",
                            )
