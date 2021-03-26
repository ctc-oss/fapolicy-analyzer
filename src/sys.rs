use cfg::SystemCfg;

use crate::api::Trust;
use crate::cfg;
use crate::rpm;
use crate::trust;

#[derive(Clone)]
pub struct System {
    pub trust_db: Vec<Trust>,
    pub system_trust: Vec<trust::Status>,
    pub ancillary_trust: Vec<trust::Status>,
}

impl System {
    pub fn boot(cfg: SystemCfg) -> System {
        // load the auth trust database
        let trust_db = trust::load_trust_db(&cfg.trust_db_path);

        // load the rpm system trust database
        let system_trust: Vec<trust::Status> = rpm::load_system_trust(&cfg.system_trust_path)
            .iter()
            .map(trust::check)
            .flatten()
            .collect();

        // load the ancillary trust file
        let ancillary_trust: Vec<trust::Status> =
            trust::load_ancillary_trust(&cfg.ancillary_trust_path)
                .iter()
                .map(trust::check)
                .flatten()
                .collect();

        System {
            trust_db,
            system_trust,
            ancillary_trust,
        }
    }
}
