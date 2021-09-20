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
