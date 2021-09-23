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

    let o: Vec<Rec> = sys
        .trust_db
        .iter()
        .filter(|(p, r)| r.is_system() && p.contains(".so"))
        .map(|e| e.1.clone())
        .take(100)
        .collect();

    let mut rng = rand::thread_rng();
    let arand = Uniform::from(0..(a.len()));
    let orand = Uniform::from(0..(o.len()));
    let orand2 = Uniform::from(2..(o.len().min(7)));
    let srand = Uniform::from(0..(s.len()));
    let urand = Uniform::from(0..(sys.users.len()));

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

        for _ in 1..(orand2.sample(&mut rng)) {
            let rec = o.iter().nth(orand.sample(&mut rng)).unwrap();
            let e = Event {
                rule_id: 0,
                dec: Decision::DenyAudit,
                perm: Permission::Any,
                uid: u.uid as i32,
                gid: u.gid as i32,
                pid: 999,
                subj: Subject {
                    parts: vec![SubjPart::Exe(t.path.clone())],
                },
                obj: Object {
                    parts: vec![ObjPart::Path(rec.trusted.path.clone())],
                },
            };
            println!("{}", e.to_string().trim());
        }
    }
}
