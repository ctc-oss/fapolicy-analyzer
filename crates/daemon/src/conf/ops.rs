use crate::conf::error::Error;
use crate::conf::{load, DB};

// Mutable
#[derive(Default, Clone, Debug)]
pub struct Changeset {
    db: DB,
    src: Option<String>,
}

impl Changeset {
    pub fn get(&self) -> &DB {
        &self.db
    }

    pub fn src(&self) -> Option<&String> {
        self.src.as_ref()
    }

    pub fn set(&mut self, text: &str) -> Result<&DB, Error> {
        match load::mem(text) {
            Ok(r) => {
                self.db = r;
                self.src = Some(text.to_string());
                Ok(&self.db)
            }
            Err(e) => Err(e),
        }
    }

    pub fn apply(&self) -> &DB {
        &self.db
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::conf::config::Entry;
    use crate::Config;
    use assert_matches::assert_matches;
    use std::error::Error;

    #[test]
    fn deserialize() -> Result<(), Box<dyn Error>> {
        let mut cs = Changeset::default();
        let txt = "permissive=0";
        let _x1 = cs.set(txt)?;
        let cfg: Config = _x1.into();
        assert_matches!(cfg.permissive, Entry::Valid(false));

        let txt = "permissive=1";
        let _x2 = cs.set(txt)?;
        let cfg: Config = _x2.into();
        assert_matches!(cfg.permissive, Entry::Valid(true));

        Ok(())
    }
}
