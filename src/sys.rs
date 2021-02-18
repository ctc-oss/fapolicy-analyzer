use crate::api::Trust;
use crate::rpm;
use crate::trust;

#[derive(Clone)]
pub struct SystemCfg {
    pub trust_db_path: Option<String>,
    pub system_trust_path: Option<String>,
    pub ancillary_trust_path: Option<String>,
}

#[derive(Clone)]
pub struct System {
    pub trust_db: Vec<Trust>,
    pub system_trust: Vec<Trust>,
    pub ancillary_trust: Vec<Trust>,
}

impl System {
    pub fn boot(cfg: SystemCfg) -> System {
        let trust_db = trust::load_trust_db(&cfg.trust_db_path);
        let system_trust = rpm::load_system_trust(&cfg.system_trust_path);
        let ancillary_trust = trust::load_ancillary_trust(&cfg.ancillary_trust_path);

        System {
            trust_db,
            system_trust,
            ancillary_trust,
        }
    }
}
