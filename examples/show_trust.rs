// Copyright Concurrent Technologies Corporation 2021
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

use fapolicy_app::app::State;
use fapolicy_app::cfg::All;
use fapolicy_trust::stat::Status::{Discrepancy, Trusted};
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let cfg = All::load()?;
    let state = State::load_checked(&cfg)?;

    state.trust_db.iter().for_each(|(p, rec)| {
        let flag = match rec.status {
            Some(Trusted(_, _)) => "T",
            Some(Discrepancy(_, _)) => "D",
            _ => "U",
        };
        println!("[{}] - {}", flag, p);
    });

    Ok(())
}
