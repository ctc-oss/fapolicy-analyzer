use crate::rpm::load_system_trust;
use api::Trust;
use fapolicyd::trust::load_ancillary_trust;

pub struct SystemCfg {
    pub ancillary_trust_path: String,
}
pub struct System {
    pub trust: Vec<Trust>,
}

impl System {
    pub fn boot(cfg: SystemCfg) -> System {
        let trust: Vec<Trust> = [
            load_system_trust(),
            load_ancillary_trust(cfg.ancillary_trust_path.as_str()),
        ]
        .concat();

        System { trust }
    }
}
