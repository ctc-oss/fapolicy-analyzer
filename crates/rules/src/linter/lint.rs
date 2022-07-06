/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::{RuleDef, DB};
use crate::linter::findings::*;
use crate::Rule;

type LintFn = fn(usize, &Rule, &DB) -> Option<String>;

pub fn lint_db(db: DB) -> DB {
    let lints: Vec<LintFn> = vec![l001, l002, l003];
    db.defs()
        .iter()
        .map(|(def, source, id)| match def {
            RuleDef::Valid(r) => {
                let x: Vec<String> = lints.iter().filter_map(|f| f(*id, r, &db)).collect();
                if x.is_empty() {
                    (source.clone(), RuleDef::Valid(r.clone()))
                } else {
                    (
                        source.clone(),
                        RuleDef::ValidWithWarning(r.clone(), x.first().unwrap().clone()),
                    )
                }
            }
            d => (source.clone(), d.clone()),
        })
        .collect::<Vec<(String, RuleDef)>>()
        .into()
}
