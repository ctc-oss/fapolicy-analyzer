use fapolicy_analyzer::event::analyze;
use fapolicy_analyzer::log::parse_event;
use fapolicy_api::trust::Trust;
use fapolicy_trust::db::{Rec, DB as TrustDB};

fn make_trust(path: &str) -> Trust {
    Trust {
        path: path.to_string(),
        size: 100,
        hash: "abc123".to_string(),
    }
}

#[test]
fn trust_status() {
    let mut trust = TrustDB::default();

    let (_, e) = parse_event("rule=4 dec=deny_syslog perm=execute uid=1004 gid=100,1002 pid=40358 exe=/bin/bash : path=/home/dave/.cargo/bin/rustc ftype=application/x-executable trust=0").ok().unwrap();
    let e1 = vec![e];

    let a1 = analyze(e1.clone(), &trust).first().unwrap().clone();
    assert_eq!(a1.subject.trust, "U");
    assert_eq!(a1.object.trust, "U");

    trust.put(Rec::new_from_system(make_trust("/bin/bash")));
    trust.put(Rec::new_from_ancillary(make_trust(
        "/home/dave/.cargo/bin/rustc",
    )));

    let a2 = analyze(e1.clone(), &trust).first().unwrap().clone();
    assert_eq!(a2.subject.trust, "ST");
    assert_eq!(a2.object.trust, "AT");
}

#[test]
fn subj_apd_status() {
    let trust = TrustDB::default();

    let (_, e1) = parse_event("rule=4 dec=deny_syslog perm=execute uid=1004 gid=100,1002 pid=40358 exe=/bin/bash : path=/home/dave/.cargo/bin/rustc ftype=application/x-executable trust=0").ok().unwrap();
    let (_, e2) = parse_event("rule=3 dec=allow_syslog perm=execute uid=1004 gid=100,1002 pid=40357 exe=/bin/bash : path=/usr/lib64/ld-2.28.so ftype=application/x-sharedlib trust=1").ok().unwrap();
    let (_, e3) = parse_event("rule=3 dec=allow_syslog perm=execute uid=1004 gid=100,1002 pid=40357 exe=/bin/bash : path=/usr/libexec/platform-python3.6 ftype=application/x-executable trust=1").ok().unwrap();

    let a1 = analyze(vec![e1.clone()], &trust).first().unwrap().clone();

    assert_eq!(a1.subject.access, "D");

    let mut allowed = vec![e2, e3];
    let a2 = analyze(allowed.clone(), &trust).first().unwrap().clone();

    assert_eq!(a2.subject.access, "A");

    allowed.push(e1);
    let a3 = analyze(allowed.clone(), &trust).first().unwrap().clone();

    assert_eq!(a3.subject.access, "P");
}

#[test]
fn obj_ad_status() {
    let trust = TrustDB::default();

    let (_, e1) = parse_event("rule=4 dec=deny_syslog perm=execute uid=1004 gid=100,1002 pid=40358 exe=/bin/bash : path=/home/dave/.cargo/bin/rustc ftype=application/x-executable trust=0").ok().unwrap();
    let (_, e2) = parse_event("rule=3 dec=allow_syslog perm=execute uid=1004 gid=100,1002 pid=40357 exe=/bin/bash : path=/usr/lib64/ld-2.28.so ftype=application/x-sharedlib trust=1").ok().unwrap();

    let a1 = analyze(vec![e1.clone()], &trust).first().unwrap().clone();
    assert_eq!(a1.object.access, "D");

    let a2 = analyze(vec![e2], &trust).first().unwrap().clone();
    assert_eq!(a2.object.access, "A");
}
