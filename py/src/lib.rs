use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::wrap_pymodule;

use trust::parse_trust_entry;
use trust::PyTrustEntry;

mod trust;
