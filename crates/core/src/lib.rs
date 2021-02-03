use api::Trust;
use fapolicyd::trust::FileTrustDB;
use rpm::db::Database;

pub struct SystemCfg {
    pub ancillary_trust_path: String,
}
pub struct System {
    trust: TrustStore,
}

struct TrustStore {
    system: Database,
    fapolicyd: FileTrustDB,
}

impl System {
    pub fn trust(&self) -> Vec<Box<dyn api::Trust>> {
        self.trust.fapolicyd.entries()
        let mut v: Vec<Box<dyn api::Trust>> = Vec::new();
        v.push(Box::new(
            self.trust.fapolicyd.entries().first().unwrap().clone(),
        ));
        v
    }

    pub fn boot(cfg: SystemCfg) -> System {
        let db = Database::load();
        let fad = FileTrustDB::from(cfg.ancillary_trust_path.as_str());

        System {
            trust: TrustStore {
                system: db,
                fapolicyd: fad,
            },
        }
    }
}
