/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::events::event::Event;
use std::slice::Iter;

#[derive(Default, Clone)]
pub struct DB {
    pub(crate) events: Vec<Event>,
}

impl DB {
    pub fn from(es: Vec<Event>) -> Self {
        DB { events: es }
    }

    /// Get an iterator to the underlying events
    pub fn iter(&self) -> Iter<'_, Event> {
        self.events.iter()
    }
}
