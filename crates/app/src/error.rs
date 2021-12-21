/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use confy::ConfyError;
use thiserror::Error;

use crate::sys;

/// An Error that can occur in this crate
#[derive(Error, Debug)]
pub enum Error {
    #[error("System error: {0}")]
    SystemError(#[from] sys::Error),
    #[error("Trust error: {0}")]
    TrustError(#[from] fapolicy_trust::error::Error),
    #[error("Rule error: {0}")]
    RuleError(#[from] fapolicy_rules::error::Error),
    #[error("Analyzer error: {0}")]
    AnalyzerError(#[from] fapolicy_analyzer::error::Error),
    #[error("XDG config error: {0}")]
    ConfigError(#[from] ConfyError),
}
