/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_daemon::stats;

#[test]
fn parse_stat_rec() {
    let rec = stats::parse("tests/data/state.0").expect("failed to parse state");
    println!("{:?}", rec);
}
