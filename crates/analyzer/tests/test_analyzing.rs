use fapolicy_analyzer::events::analysis::Analysis;
use fapolicy_analyzer::events::db::DB as EventDB;
use fapolicy_analyzer::events::event::{Event, Perspective};
use fapolicy_api::trust::Trust;
use fapolicy_rules::{Decision, Object, Permission, Subject};
use fapolicy_trust::db::{Rec, DB as TrustDB};

const BASH_PATH: &str = "/bin/bash";

fn make_trust(path: &str) -> Trust {
    Trust {
        path: path.to_string(),
        size: 100,
        hash: "abc123".to_string(),
    }
}

fn bash_allowed(o: &str, uid: i32, gid: i32) -> Event {
    bash_event(Decision::Allow, o, uid, gid)
}

fn bash_denied(o: &str, uid: i32, gid: i32) -> Event {
    bash_event(Decision::Deny, o, uid, gid)
}

fn bash_event(dec: Decision, o: &str, uid: i32, gid: i32) -> Event {
    event(BASH_PATH, dec, o, uid, gid)
}

fn event(s: &str, dec: Decision, o: &str, uid: i32, gid: i32) -> Event {
    Event {
        rule_id: 1,
        dec,
        perm: Permission::Any,
        uid,
        gid: vec![gid],
        pid: 1,
        subj: Subject::from_exe(s),
        obj: Object::from_path(o),
    }
}

fn analyze_from_user(es: &[Event], uid: i32, t: &TrustDB) -> Analysis {
    analyze(Vec::from(es), Perspective::User(uid), t)
        .first()
        .unwrap()
        .clone()
}

fn analyze_from_group(es: &[Event], gid: i32, t: &TrustDB) -> Analysis {
    analyze(Vec::from(es), Perspective::Group(gid), t)
        .first()
        .unwrap()
        .clone()
}

fn analyze_from_subject(es: &[Event], s: &str, t: &TrustDB) -> Vec<Analysis> {
    analyze(Vec::from(es), Perspective::Subject(s.into()), t)
}

fn analyze(es: Vec<Event>, from: Perspective, t: &TrustDB) -> Vec<Analysis> {
    fapolicy_analyzer::events::analysis::analyze(&EventDB::from(es), from, t)
}

#[test]
fn trust_status() {
    let mut trust = TrustDB::default();

    let uid = 1004;
    let log = vec![bash_allowed("/foo/bar", uid, 1003)];

    let a1 = analyze_from_user(&log, uid, &trust);
    assert_eq!(a1.subject.trust, "U");
    assert_eq!(a1.object.trust, "U");

    trust.put(Rec::new_from_system(make_trust("/bin/bash")));
    trust.put(Rec::new_from_ancillary(make_trust("/foo/bar")));

    let a2 = analyze_from_user(&log, uid, &trust);
    assert_eq!(a2.subject.trust, "ST");
    assert_eq!(a2.object.trust, "AT");
}

#[test]
fn simple_subj_apd_status() {
    let trust = TrustDB::default();

    let uid = 1004;
    let log = vec![bash_denied("/foo/bar", uid, 1003)];

    let a1 = analyze_from_user(&log, uid, &trust);

    assert_eq!(a1.subject.access, "D");

    let mut log = vec![
        bash_allowed("/foo/bin", uid, 1003),
        bash_allowed("/foo/baz", uid, 1003),
    ];
    let a2 = analyze_from_user(&log, uid, &trust);

    assert_eq!(a2.subject.access, "A");

    log.push(bash_denied("/foo/bar", uid, 1003));
    let a3 = analyze_from_user(&log, uid, &trust);

    assert_eq!(a3.subject.access, "P");
}

#[test]
fn simple_obj_ad_status() {
    let trust = TrustDB::default();

    let uid = 1004;
    let e1 = bash_denied("/foo/bar", uid, 1003);
    let e2 = bash_allowed("/foo/bin", uid, 1003);

    let a1 = analyze_from_user(&*vec![e1], uid, &trust);
    assert_eq!(a1.object.access, "D");

    let a2 = analyze_from_user(&*vec![e2], uid, &trust);
    assert_eq!(a2.object.access, "A");
}

#[test]
fn user_subj_apd_status() {
    let trust = TrustDB::default();

    let uid = 1004;
    let e1 = bash_denied("/foo/bar", uid, 1003);
    let e2 = bash_allowed("/foo/bin", uid, 1003);
    let e3 = bash_allowed("/foo/baz", uid, 1003);

    let a1 = analyze_from_user(&*vec![e1.clone()], uid, &trust);

    assert_eq!(a1.subject.access, "D");

    let mut allowed = vec![e2, e3];
    let a2 = analyze_from_user(&allowed, uid, &trust);

    assert_eq!(a2.subject.access, "A");

    allowed.push(e1);
    let a3 = analyze_from_user(&allowed, uid, &trust);

    assert_eq!(a3.subject.access, "P");
}

#[test]
fn user_obj_ad_status() {
    let trust = TrustDB::default();

    let uid = 1004;
    let e1 = bash_denied("/foo/bar", uid, 1003);
    let e2 = bash_allowed("/foo/bin", uid, 1003);

    let a1 = analyze_from_user(&*vec![e1], uid, &trust);
    assert_eq!(a1.object.access, "D");

    let a2 = analyze_from_user(&*vec![e2], uid, &trust);
    assert_eq!(a2.object.access, "A");
}

#[test]
fn group_subj_apd_status_1() {
    let trust = TrustDB::default();

    let mut log = vec![bash_denied("/foo/bar", 1, 1003)];
    let a1 = analyze_from_group(&log, 1003, &trust);

    assert_eq!(a1.subject.access, "D");

    log.push(bash_allowed("/foo/bar", 2, 1003));
    let a2 = analyze_from_group(&log, 1003, &trust);

    assert_eq!(a2.subject.access, "P");
}

#[test]
fn group_subj_apd_status_2() {
    let trust = TrustDB::default();

    let mut log = vec![bash_allowed("/foo/bip", 3, 1004)];
    let a1 = analyze_from_group(&log, 1004, &trust);

    assert_eq!(a1.subject.access, "A");

    log.push(bash_denied("/foo/bip", 4, 1005));
    let a2 = analyze_from_group(&log, 1004, &trust);

    assert_eq!(a2.subject.access, "A");

    log.push(bash_denied("/foo/bip", 5, 1004));
    let a2 = analyze_from_group(&log, 1004, &trust);

    assert_eq!(a2.subject.access, "P");
}

#[test]
fn subj_perspective() {
    let trust = TrustDB::default();

    let log = vec![
        event("/foo", Decision::Allow, "x", 1, 999),
        event("/foo", Decision::Allow, "x", 2, 999),
        event("/bar", Decision::Allow, "x", 1, 888),
        event("/bar", Decision::Allow, "x", 1, 999),
        event("/baz", Decision::Allow, "x", 1, 999),
        event("/baz", Decision::Deny, "x", 2, 999),
        event("/nope", Decision::Deny, "x", 1, 999),
        event("/nada", Decision::Deny, "x", 2, 999),
    ];

    let a = analyze_from_subject(&log, "/foo", &trust);
    assert_eq!(a.len(), 2);

    let a = analyze_from_subject(&log, "/bar", &trust);
    assert_eq!(a.len(), 2);

    let a = analyze_from_subject(&log, "/baz", &trust);
    assert_eq!(a.len(), 2);

    let a = analyze_from_subject(&log, "/nope", &trust);
    assert_eq!(a.len(), 1);

    let a = analyze_from_subject(&log, "/nada", &trust);
    assert_eq!(a.len(), 1);
}
