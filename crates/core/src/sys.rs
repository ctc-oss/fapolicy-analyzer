use api::Trust;

pub struct SystemCfg {
    pub ancillary_trust_path: String,
}
pub struct System {
    trust: TrustStore,
}

struct TrustStore {}

impl System {
    pub fn boot(cfg: SystemCfg) -> System {
        System {
            trust: TrustStore {},
        }
    }
}
