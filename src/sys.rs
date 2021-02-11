use crate::api::Trust;
use crate::rpm::load_system_trust;
use crate::trust::load_ancillary_trust;

pub struct SystemCfg {
    pub ancillary_trust_path: Option<String>,
    pub system_trust_path: Option<String>,
}

#[derive(Clone)]
pub struct System {
    pub trust: Vec<Trust>,
}

impl System {
    pub fn boot(cfg: SystemCfg) -> System {
        let trust: Vec<Trust> = [
            load_system_trust(&cfg.system_trust_path),
            load_ancillary_trust(&cfg.ancillary_trust_path),
        ]
        .concat();

        System { trust }
    }
}
