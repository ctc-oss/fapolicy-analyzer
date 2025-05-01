# Copyright Concurrent Technologies Corporation 2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import tomli
from rx import of
from rx.core.pipe import pipe
from rx.operators import catch, map

from fapolicy_analyzer import config_file_path
from fapolicy_analyzer.redux import (
    Action,
    ReduxFeatureModule,
    combine_epics,
    create_feature_module,
    of_type,
)
from fapolicy_analyzer.ui.actions import (
    REQUEST_APP_CONFIG,
    error_app_config,
    received_app_config,
)
from fapolicy_analyzer.ui.reducers import application_reducer

APPLICATION_FEATURE = "application"


def create_application_feature() -> ReduxFeatureModule:
    """
    Redux feature used for application level calls to the rust layer.
    """

    def _get_app_config(_: Action) -> Action:
        path = config_file_path()
        with open(path, "r") as f:
            config = tomli.load(f)
        return received_app_config(config.get("ui", {}))

    request_app_config_epic = pipe(
        of_type(REQUEST_APP_CONFIG),
        map(_get_app_config),
        catch(lambda ex, source: of(error_app_config(str(ex)))),
    )

    application_epic = combine_epics(
        request_app_config_epic,
    )
    return create_feature_module(
        APPLICATION_FEATURE, application_reducer, application_epic
    )
