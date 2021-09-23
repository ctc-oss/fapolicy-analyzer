use fapolicy_analyzer::log::Event;
use fapolicy_analyzer::rules::{Decision, Object, Permission, Subject};
use fapolicy_analyzer::rules::{ObjPart, SubjPart};
use fapolicy_app::app::State;
use fapolicy_app::cfg::All;
use fapolicy_trust::db::Rec;
use rand::distributions::{Distribution, Uniform};

fn main() {
    let cfg = All::load();
    let sys = State::load(&cfg).expect("cant load state");

    let s: Vec<Rec> = sys
        .trust_db
        .iter()
        .filter(|(p, r)| r.is_system() && p.ends_with(".sh"))
        .map(|e| e.1.clone())
        .take(10)
        .collect();

    let a: Vec<Rec> = sys
        .trust_db
        .iter()
        .filter(|(_, r)| r.is_ancillary())
        .map(|e| e.1.clone())
        .collect();

    let mut rng = rand::thread_rng();
    let arand = Uniform::from(1..(a.len()));
    let srand = Uniform::from(1..(s.len()));
    let urand = Uniform::from(1..(sys.users.len()));

    for i in 0..100 {
        let u = sys.users.iter().nth(urand.sample(&mut rng)).unwrap();
        let t = if i % 2 == 0 {
            s.iter()
                .map(|r| r.trusted.clone())
                .nth(srand.sample(&mut rng))
                .unwrap()
                .clone()
        } else {
            a.iter()
                .map(|r| r.trusted.clone())
                .nth(arand.sample(&mut rng))
                .unwrap()
                .clone()
        };
        let (o, _) = sys.trust_db.iter().nth(i + 100).unwrap();

        let e = Event {
            rule_id: 0,
            dec: Decision::DenyAudit,
            perm: Permission::Any,
            uid: u.uid as i32,
            gid: u.gid as i32,
            pid: 999,
            subj: Subject {
                parts: vec![SubjPart::Exe(t.path)],
            },
            obj: Object {
                parts: vec![ObjPart::Path(o.clone())],
            },
        };
        println!("{}", e.to_string().trim());
    }
}
