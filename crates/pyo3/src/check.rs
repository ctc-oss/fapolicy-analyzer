/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::system::PySystem;
use fapolicy_trust::db::{Rec, DB};
use pyo3::prelude::*;
use std::sync::mpsc;
use std::thread;

use crate::trust::PyTrust;
use fapolicy_trust::stat::{check, Status};

enum Update {
    Items(Vec<Status>),
    Done,
}

// keeping a max of 100 batches for now
const FIXED_BATCH_COUNT: usize = 100;

#[derive(Debug, Default)]
struct BatchConfig {
    thread_cnt: usize,
    thread_load: usize,
    batch_cnt: usize,
    batch_load: usize,
}

pub fn filter_db<F>(db: &DB, f: F) -> Vec<Rec>
where
    F: FnMut(&&Rec) -> bool,
{
    db.values().into_iter().filter(f).cloned().collect()
}

#[pyfunction]
fn check_ancillary_trust(system: &PySystem, update: PyObject, done: PyObject) -> PyResult<usize> {
    let recs = filter_db(&system.rs.trust_db, |r| r.is_ancillary());
    check_disk_trust(recs, update, done)
}

#[pyfunction]
fn check_system_trust(system: &PySystem, update: PyObject, done: PyObject) -> PyResult<usize> {
    let recs = filter_db(&system.rs.trust_db, |r| r.is_system());
    check_disk_trust(recs, update, done)
}

#[pyfunction]
fn check_all_trust(system: &PySystem, update: PyObject, done: PyObject) -> PyResult<usize> {
    let recs: Vec<_> = system.rs.trust_db.values().into_iter().cloned().collect();
    check_disk_trust(recs, update, done)
}

fn callback_on_done(done: PyObject) {
    Python::with_gil(|py| {
        if done.call0(py).is_err() {
            eprintln!("failed to make 'done' callback");
        }
    })
}

fn check_disk_trust(recs: Vec<Rec>, update: PyObject, done: PyObject) -> PyResult<usize> {
    if recs.is_empty() {
        thread::spawn(move || {
            callback_on_done(done);
        });
        return Ok(0);
    }

    // determine batch model based on the total recs to be checked
    let batch_cfg = calculate_batch_config(recs.len());
    eprintln!(
        "BatchConf: recs: {}, tc:{}, tl:{}, bc:{}, bl:{}",
        recs.len(),
        batch_cfg.thread_cnt,
        batch_cfg.thread_load,
        batch_cfg.batch_cnt,
        batch_cfg.batch_load
    );

    // 1. split the total recs into sized batches
    // 2. split the batches into chunks based on thread load
    let batches: Vec<_> = recs.chunks(batch_cfg.batch_load).map(Vec::from).collect();
    let batches: Vec<_> = batches
        .chunks(batch_cfg.thread_load)
        .map(Vec::from)
        .collect();

    if batch_cfg.thread_cnt != batches.len() {
        eprintln!(
            "warning: thread_cnt {} does not match batch count {}",
            batch_cfg.thread_cnt,
            batches.len()
        );
    }

    let (tx, rx) = mpsc::channel();

    // the on-data-available callback thread
    // this aggregates all batch threads back into the single callback
    thread::spawn(move || {
        let mut cnt = 0;
        loop {
            if let Ok(u) = rx.recv() {
                match u {
                    Update::Items(i) => {
                        cnt += i.len();
                        let r: Vec<_> = i.into_iter().map(PyTrust::from).collect();
                        Python::with_gil(|py| {
                            if update.call1(py, (r, cnt)).is_err() {
                                eprintln!("failed make 'update' callback");
                            }
                        });
                    }
                    Update::Done => break,
                };
            }
        }

        callback_on_done(done);
    });

    // at this point data is organized into per-thread batches
    // spawn a thread for each of these and loop over the threads load
    // keep track of the threads to observe when processing is complete
    let mut handles = vec![];
    for thread_load in batches {
        let ttx = tx.clone();
        let t = thread::spawn(move || {
            for batch in thread_load {
                let updates = batch
                    .into_iter()
                    .map(|r| check(&r.trusted).unwrap_or(Status::Missing(r.trusted)))
                    .collect::<Vec<_>>();
                if ttx.send(Update::Items(updates)).is_err() {
                    eprintln!("failed to send Items msg");
                };
            }
        });
        handles.push(t);
    }

    // use the tracked threads to observe when processing is complete
    thread::spawn(move || {
        for handle in handles {
            if handle.join().is_err() {
                eprintln!("failed to join update handle");
            };
        }
        if tx.send(Update::Done).is_err() {
            eprintln!("failed to send Done msg");
        };
    });

    Ok(recs.len())
}

fn calculate_batch_config(rec_sz: usize) -> BatchConfig {
    if rec_sz == 0 {
        return BatchConfig::default();
    }

    let (batch_load, batch_cnt) = match (rec_sz / FIXED_BATCH_COUNT, rec_sz % FIXED_BATCH_COUNT) {
        // less than FIXED_BATCH_COUNT, use a single batch
        (0, rem) => (rem, 1),
        // batches are all even
        (sz, 0) => (sz, FIXED_BATCH_COUNT),
        // batched out with remainder
        (sz, _) => (sz + 1, FIXED_BATCH_COUNT),
    };

    // thread count is adjusted based on batch size
    // larger batches result in more threads
    let thread_cnt = match (batch_cnt, batch_load) {
        // one batch, one thread
        (1, _) => 1,
        // small batches get 5 threads
        (_, s) if s <= 1000 => 5,
        // large batches get 10 threads
        _ => 10,
    };

    // thread load is number of batches per thread
    let thread_load = batch_cnt / thread_cnt;

    BatchConfig {
        thread_cnt,
        thread_load,
        batch_cnt,
        batch_load,
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(check_system_trust, m)?)?;
    m.add_function(wrap_pyfunction!(check_ancillary_trust, m)?)?;
    m.add_function(wrap_pyfunction!(check_all_trust, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn batch_load_0() {
        let num = 0;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 0);
        assert_eq!(cfg.batch_load, 0);
        assert_eq!(cfg.thread_cnt, 0);
        assert_eq!(cfg.thread_load, 0);
    }

    #[test]
    fn batch_load_1() {
        let num = 1;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 1);
        assert_eq!(cfg.batch_load, 1);
        assert_eq!(cfg.thread_cnt, 1);
        assert_eq!(cfg.thread_load, 1);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
        assert_eq!(1, cfg.thread_load * cfg.thread_cnt);
    }

    #[test]
    fn batch_load_9() {
        let num = 9;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 1);
        assert_eq!(cfg.batch_load, 9);
        assert_eq!(cfg.thread_cnt, 1);
        assert_eq!(cfg.thread_load, 1);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
    }

    #[test]
    fn batch_load_42() {
        let num = 42;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 1);
        assert_eq!(cfg.batch_load, 42);
        assert_eq!(cfg.thread_cnt, 1);
        assert_eq!(cfg.thread_load, 1);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
    }

    #[test]
    fn batch_load_99() {
        let num = 99;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 1);
        assert_eq!(cfg.batch_load, 99);
        assert_eq!(cfg.thread_cnt, 1);
        assert_eq!(cfg.thread_load, 1);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
    }

    #[test]
    fn batch_load_501() {
        let num = 501;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 100);
        assert_eq!(cfg.batch_load, 6);
        assert_eq!(cfg.thread_cnt, 5);
        assert_eq!(cfg.thread_load, 20);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
        assert_eq!(100, cfg.thread_load * cfg.thread_cnt);
    }

    #[test]
    fn batch_load_999ish() {
        let num = 999;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 100);
        assert_eq!(cfg.batch_load, 10);
        assert_eq!(cfg.thread_cnt, 5);
        assert_eq!(cfg.thread_load, 20);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
        assert_eq!(100, cfg.thread_load * cfg.thread_cnt);

        let num = 998;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 100);
        assert_eq!(cfg.batch_load, 10);
        assert_eq!(cfg.thread_cnt, 5);
        assert_eq!(cfg.thread_load, 20);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
        assert_eq!(100, cfg.thread_load * cfg.thread_cnt);

        let num = 1000;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 100);
        assert_eq!(cfg.batch_load, 10);
        assert_eq!(cfg.thread_cnt, 5);
        assert_eq!(cfg.thread_load, 20);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
        assert_eq!(100, cfg.thread_load * cfg.thread_cnt);
    }

    #[test]
    fn batch_load_19999() {
        let num = 19999;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 100);
        assert_eq!(cfg.batch_load, 200);
        assert_eq!(cfg.thread_cnt, 5);
        assert_eq!(cfg.thread_load, 20);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
        assert_eq!(100, cfg.thread_load * cfg.thread_cnt);
    }

    #[test]
    fn batch_load_60000() {
        let num = 60000;
        let cfg = calculate_batch_config(num);

        // assert the basic configuration
        assert_eq!(cfg.batch_cnt, 100);
        assert_eq!(cfg.batch_load, 600);
        assert_eq!(cfg.thread_cnt, 5);
        assert_eq!(cfg.thread_load, 20);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
        assert_eq!(100, cfg.thread_load * cfg.thread_cnt);
    }

    #[test]
    fn batch_load_112020() {
        let num = 112020;
        let cfg = calculate_batch_config(num);

        // assert the basic configuration
        assert_eq!(cfg.batch_cnt, 100);
        assert_eq!(cfg.batch_load, 1121);
        assert_eq!(cfg.thread_cnt, 10);
        assert_eq!(cfg.thread_load, 10);

        // assert that we are within one batch of the total
        assert!(num <= cfg.batch_cnt * cfg.batch_load);
        assert!(num / cfg.batch_cnt <= cfg.batch_load);
        assert_eq!(100, cfg.thread_load * cfg.thread_cnt);
    }
}
