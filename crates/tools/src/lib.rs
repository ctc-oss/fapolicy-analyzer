// Copyright Concurrent Technologies Corporation 2024
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

use human_panic::{setup_panic, Metadata};

pub fn setup_human_panic() {
    setup_panic!(
        Metadata::new(env!("CARGO_PKG_NAME"), env!("CARGO_PKG_VERSION"))
            .authors("CTC-OSS and contributors")
            .homepage("https://github.com/ctc-oss/fapolicy-analyzer")
            .support(
                [
                    "- Open a GitHub issue on the fapolicy-analyzer project page",
                    "- Open a Red Hat Bugzilla issue for the fapolicy-analyzer package"
                ]
                .join("\n")
            )
    );
}
