/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_app::app::State;
use fapolicy_app::cfg::All;
use fapolicy_trust::ops::Changeset;

#[test]
fn test_change_trust_state() {
    let cfg = All::default();
    let s = State::empty(&cfg);
    assert!(s.trust_db.is_empty());

    let mut xs = Changeset::new();
    xs.add("tests/data/runme.sh");
    assert_eq!(xs.len(), 1);

    let s = s.apply_trust_changes(xs);
    assert_eq!(s.trust_db.len(), 1);
}
