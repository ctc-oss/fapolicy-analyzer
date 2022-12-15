/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::system::PySystem;
use pyo3::prelude::*;
use std::sync::mpsc;
use std::thread;

use crate::trust::PyTrust;
use fapolicy_trust::stat::{check, Status};

enum Update {
    Items(Vec<Status>),
    Done,
}

#[derive(Debug)]
struct BatchConfig {
    thread_cnt: usize,
    thread_load: usize,
    batch_cnt: usize,
    batch_load: usize,
}

// (chunk_size, thread_count)
fn calculate_batch_config(rec_sz: usize) -> BatchConfig {
    let (batch_load, batch_cnt) = match (rec_sz / 100, rec_sz % 100) {
        (0, _) => (rec_sz, 1),
        (sz, 0) => (sz, rec_sz / sz),
        (sz, rem) => match rem / (rec_sz / sz) {
            0 => (sz + 1, rec_sz / sz),
            a => (sz + a, rec_sz / sz),
        },
    };

    // thread count is adjusted based on batch size
    // larger batches result in more threads
    let thread_cnt = match (batch_cnt, batch_load) {
        // one batch, one thread
        (1, _) => 1,
        // small batches get 4 threads
        (_, s) if s <= 10 => 4,
        // medium batches get 10 threads
        (_, s) if s <= 100 => 10,
        // large batches get 20 threads
        (_, s) if s <= 200 => 10,
        // xl batches get 25 threads
        _ => 25,
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

#[pyfunction]
fn check_disk_trust(system: &PySystem, update: PyObject, done: PyObject) -> PyResult<usize> {
    let recs: Vec<_> = system
        .rs
        .trust_db
        .values()
        .into_iter()
        .map(|r| r.clone())
        .collect();

    // determine batch model based on the total recs to be checked
    let batch_cfg = calculate_batch_config(recs.len());

    // 1. separate the total recs into sized batches
    // 2. separate batches into appropriate thread load
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
                        cnt += 1;
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

        Python::with_gil(|py| {
            if done.call0(py).is_err() {
                eprintln!("failed to make 'done' callback");
            }
        });
    });

    let mut handles = vec![];
    // at this point data is organized into per-thread batches
    // spawn a thread for each of these and loop over the threads load
    for thread_load in batches {
        let ttx = tx.clone();
        let t = thread::spawn(move || {
            for batch in thread_load {
                let updates = batch
                    .into_iter()
                    .flat_map(|r| check(&r.trusted))
                    .collect::<Vec<_>>();
                if ttx.send(Update::Items(updates)).is_err() {
                    eprintln!("failed to send Items msg");
                };
            }
        });
        handles.push(t);
    }

    let ttx = tx.clone();
    thread::spawn(move || {
        for handle in handles {
            if handle.join().is_err() {
                eprintln!("failed to join update handle");
            };
        }
        if ttx.send(Update::Done).is_err() {
            eprintln!("failed to send Done msg");
        };
    });

    Ok(batch_cfg.batch_cnt)
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(check_disk_trust, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn batch_load_1() {
        let cfg = calculate_batch_config(1);
        assert_eq!(cfg.batch_cnt, 1);
        assert_eq!(cfg.batch_load, 1);
        assert_eq!(cfg.thread_cnt, 1);
        assert_eq!(cfg.thread_load, 1);
    }

    #[test]
    fn batch_load_9() {
        let cfg = calculate_batch_config(9);
        assert_eq!(cfg.batch_cnt, 1);
        assert_eq!(cfg.batch_load, 9);
        assert_eq!(cfg.thread_cnt, 1);
        assert_eq!(cfg.thread_load, 1);
    }

    #[test]
    fn batch_load_99() {
        let cfg = calculate_batch_config(99);
        assert_eq!(cfg.batch_cnt, 1);
        assert_eq!(cfg.batch_load, 99);
        assert_eq!(cfg.thread_cnt, 1);
        assert_eq!(cfg.thread_load, 1);
    }

    #[test]
    fn batch_load_999() {
        let cfg = calculate_batch_config(999);
        assert_eq!(cfg.batch_cnt, 99);
        assert_eq!(cfg.batch_load, 10);
        assert_eq!(cfg.thread_cnt, 10);
        assert_eq!(cfg.thread_load, 9);
    }

    #[test]
    fn batch_load_19999() {
        let num = 19999;
        let cfg = calculate_batch_config(num);
        assert_eq!(cfg.batch_cnt, 99);
        assert_eq!(cfg.batch_load, 200);
        assert_eq!(cfg.thread_cnt, 20);
        assert_eq!(cfg.thread_load, 4);
    }

    #[test]
    fn batch_load_112020() {
        let num = 112020;
        let cfg = calculate_batch_config(num);

        // assert the basic configuration
        assert_eq!(cfg.batch_cnt, 100);
        assert_eq!(cfg.batch_load, 1121);
        assert_eq!(cfg.thread_cnt, 25);
        assert_eq!(cfg.thread_load, 4);

        // assert that we are within one batch of the total
        assert!(num < cfg.batch_cnt * cfg.batch_load);
        assert!(num + cfg.batch_load > cfg.batch_cnt * cfg.batch_load);

        assert_eq!(100, cfg.thread_load * cfg.thread_cnt);
    }
}
