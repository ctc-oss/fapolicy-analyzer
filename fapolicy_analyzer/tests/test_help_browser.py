# Copyright Concurrent Technologies Corporation 2022
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

import context  # noqa: F401 # isort: skip


from fapolicy_analyzer.ui.help_browser import HelpBrowser


def test_loads_url(mocker):
    url = "https://github.com/"
    mock_load = mocker.patch("fapolicy_analyzer.ui.help_browser.HelpBrowser.load_uri")
    HelpBrowser(uri=url)
    mock_load.assert_called_with(url)
