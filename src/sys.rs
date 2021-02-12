use crate::api::Trust;
use crate::rpm::load_system_trust;
use crate::trust::load_ancillary_trust;

pub struct SystemCfg {
    pub ancillary_trust_path: Option<String>,
    pub system_trust_path: Option<String>,
}

#[derive(Clone)]
pub struct System {
    pub system_trust: Vec<Trust>,
    pub ancillary_trust: Vec<Trust>,
}

impl System {
    pub fn boot(cfg: SystemCfg) -> System {
        let system_trust = load_system_trust(&cfg.system_trust_path);
        let ancillary_trust = load_ancillary_trust(&cfg.ancillary_trust_path);

        System {
            system_trust,
            ancillary_trust,
        }
    }
}
