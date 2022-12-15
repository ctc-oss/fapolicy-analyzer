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

#[pyfunction]
fn check_disk_trust(db: &PySystem, update: PyObject, done: PyObject) -> PyResult<()> {
    let recs: Vec<_> = db
        .rs
        .trust_db
        .values()
        .into_iter()
        .map(|r| r.clone())
        .collect();

    let sz = recs.len() / 100;
    let chunks = recs.chunks(sz + 1);

    let (tx, rx) = mpsc::channel();
    let mut handles = vec![];

    for chunk in chunks {
        let ttx = tx.clone();
        let recs = chunk.to_vec();
        let t = thread::spawn(move || {
            let updates = recs
                .into_iter()
                .flat_map(|r| check(&r.trusted))
                .collect::<Vec<_>>();
            if ttx.send(Update::Items(updates)).is_err() {
                eprintln!("failed to send Items msg");
            };
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

    Ok(())
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(check_disk_trust, m)?)?;
    Ok(())
}
