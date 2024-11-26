use crate::error::Error;
use crate::error::Error::ParseStatsError;
use nom::bytes::complete::tag;
use nom::character::complete::digit1;
use nom::sequence::{delimited, separated_pair, terminated};
use notify::event::{DataChange, ModifyKind};
use notify::{Config, Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher};
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use std::sync::mpsc::Receiver;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

#[derive(Debug, Default, Clone)]
pub struct Rec {
    permissive: bool,
    q_size: i32,
    inter_thread_max_queue_depth: i32,
    allowed_accesses: i32,
    denied_accesses: i32,
    trust_db_max_pages: i32,
    trust_db_pages_in_use: (i32, f32),
    subject_cache_size: i32,
    subject_slots_in_use: (i32, f32),
    subject_hits: i32,
    subject_misses: i32,
    subject_evictions: (i32, f32),
    object_cache_size: i32,
    object_slots_in_use: (i32, f32),
    object_hits: i32,
    object_misses: i32,
    object_evictions: (i32, f32),
}

#[derive(Debug, Default)]
pub struct Avg {
    count: i32,
    q_size: i32,
    inter_thread_max_queue_depth: i32,
    allowed_accesses: i32,
    denied_accesses: i32,
    trust_db_max_pages: i32,
    trust_db_pages_in_use: i32,
    subject_cache_size: i32,
    subject_slots_in_use: i32,
    subject_hits: i32,
    subject_misses: i32,
    subject_evictions: i32,
    object_cache_size: i32,
    object_slots_in_use: i32,
    object_hits: i32,
    object_misses: i32,
    object_evictions: i32,
    duration: Duration,
}

impl Avg {
    pub fn add(&mut self, rec: &Rec) {
        self.count += 1;
        self.q_size += rec.q_size;
        self.inter_thread_max_queue_depth += rec.inter_thread_max_queue_depth;
        self.allowed_accesses += rec.allowed_accesses;
        self.denied_accesses += rec.denied_accesses;
        self.trust_db_max_pages += rec.trust_db_max_pages;
        self.trust_db_pages_in_use += rec.trust_db_pages_in_use.0;
        self.subject_cache_size += rec.subject_cache_size;
        self.subject_slots_in_use += rec.subject_slots_in_use.0;
        self.subject_hits += rec.subject_hits;
        self.subject_misses += rec.subject_misses;
        self.subject_evictions += rec.subject_evictions.0;
        self.object_cache_size += rec.object_cache_size;
        self.object_slots_in_use += rec.object_slots_in_use.0;
        self.object_hits += rec.object_hits;
        self.object_misses += rec.object_misses;
        self.object_evictions += rec.object_evictions.0;
    }

    pub fn reduce(&self) -> Self {
        let n = self.count;
        Self {
            count: self.q_size / n,
            q_size: self.q_size / n,
            inter_thread_max_queue_depth: self.inter_thread_max_queue_depth / n,
            allowed_accesses: self.allowed_accesses / n,
            denied_accesses: self.denied_accesses / n,
            trust_db_max_pages: self.trust_db_max_pages / n,
            trust_db_pages_in_use: self.trust_db_pages_in_use / n,
            subject_cache_size: self.subject_cache_size / n,
            subject_slots_in_use: self.subject_slots_in_use / n,
            subject_hits: self.subject_hits / n,
            subject_misses: self.subject_misses / n,
            subject_evictions: self.subject_evictions / n,
            object_cache_size: self.object_cache_size / n,
            object_slots_in_use: self.object_slots_in_use / n,
            object_hits: self.object_hits / n,
            object_misses: self.object_misses / n,
            object_evictions: self.object_evictions / n,
            duration: Default::default(),
        }
    }
}

#[derive(Debug, Default)]
pub struct Db {
    entries: Vec<(Instant, Rec)>,
}

impl Db {
    pub fn prune(&mut self, now: Instant, ttl: Duration) {
        self.entries.retain(|(i, _)| now.duration_since(*i) < ttl);
    }

    pub fn insert(&mut self, now: Instant, rec: Rec) {
        self.entries.push((now, rec));
    }

    pub fn pruned_insert(&mut self, now: Instant, ttl: Duration, rec: Rec) {
        self.insert(now, rec);
        self.prune(now, ttl);
    }

    pub fn avg(&self, interval: Duration) -> Avg {
        let now = Instant::now();
        let subset = self
            .entries
            .iter()
            .filter(|(i, _)| now.duration_since(*i) < interval)
            .fold(Avg::default(), |mut acc, (_, r)| {
                acc.add(r);
                acc
            });
        subset.reduce()
    }
}

pub fn read(path: &str, db: Arc<Mutex<Db>>) -> Result<Receiver<Rec>, Error> {
    let (ext_tx, ext_rx) = std::sync::mpsc::channel();
    let (tx, rx) = std::sync::mpsc::channel();

    thread::spawn({
        let path = path.to_owned();
        move || {
            let mut watcher = Box::new(RecommendedWatcher::new(tx, Config::default()).unwrap());
            watcher
                .watch(Path::new(&path), RecursiveMode::NonRecursive)
                .unwrap();

            loop {
                if let Ok(Ok(Event {
                    kind: EventKind::Modify(ModifyKind::Data(_)),
                    ..
                })) = rx.recv()
                {
                    let rec = parse(&path).expect("rec parse error");
                    ext_tx.send(rec).unwrap();
                }
            }
        }
    });

    Ok(ext_rx)
}

pub fn parse(path: &str) -> Result<Rec, Error> {
    let f = File::open(path)?;
    let buf = BufReader::new(f);
    let lines = buf.lines();

    let mut rec = Rec::default();
    for line in lines {
        let line = line?;
        let line = line.trim();
        match line.split_once(':').map(|(k, v)| (k.trim(), v.trim())) {
            Some(("Permissive", v)) => {
                rec.permissive = v
                    .parse()
                    .map_err(|_| ParseStatsError("permissive".to_owned()))?
            }
            Some(("q_size", v)) => {
                rec.q_size = v
                    .parse()
                    .map_err(|_| ParseStatsError("q_size".to_owned()))?
            }
            Some(("Inter-thread max queue depth", v)) => {
                rec.inter_thread_max_queue_depth = v
                    .parse()
                    .map_err(|_| ParseStatsError("Inter-thread max queue depth".to_owned()))?
            }
            Some(("Allowed accesses", v)) => {
                rec.allowed_accesses = v
                    .parse()
                    .map_err(|_| ParseStatsError("Allowed accesses".to_owned()))?
            }
            Some(("Denied accesses", v)) => {
                rec.denied_accesses = v
                    .parse()
                    .map_err(|_| ParseStatsError("Denied accesses".to_owned()))?
            }
            Some(("Trust database max pages", v)) => {
                rec.trust_db_max_pages = v
                    .parse()
                    .map_err(|_| ParseStatsError("Trust database max pages".to_owned()))?
            }
            Some(("Trust database pages in use", v)) => {
                rec.trust_db_pages_in_use = with_pct(v)
                    .map_err(|_| ParseStatsError("Trust database pages in use".to_owned()))?
                    .1
            }
            Some(("Subject cache size", v)) => {
                rec.subject_cache_size = v
                    .parse()
                    .map_err(|_| ParseStatsError("Subject cache size".to_owned()))?
            }
            Some(("Subject slots in use", v)) => {
                rec.subject_slots_in_use = with_pct(v)
                    .map_err(|_| ParseStatsError("permissive".to_owned()))?
                    .1
            }
            Some(("Subject hits", v)) => {
                rec.subject_hits = v
                    .parse()
                    .map_err(|_| ParseStatsError("Subject hits".to_owned()))?
            }
            Some(("Subject misses", v)) => {
                rec.subject_misses = v.parse().map_err(|_| ParseStatsError("v".to_owned()))?
            }
            Some(("Subject evictions", v)) => {
                rec.subject_evictions = with_pct(v)
                    .map_err(|_| ParseStatsError("Subject evictions".to_owned()))?
                    .1
            }
            Some(("Object cache size", v)) => {
                rec.object_cache_size = v
                    .parse()
                    .map_err(|_| ParseStatsError("Object cache size".to_owned()))?
            }
            Some(("Object slots in use", v)) => {
                rec.object_slots_in_use = with_pct(v)
                    .map_err(|_| ParseStatsError("Object slots in use".to_owned()))?
                    .1
            }
            Some(("Object hits", v)) => {
                rec.object_hits = v
                    .parse()
                    .map_err(|_| ParseStatsError("Object hits".to_owned()))?
            }
            Some(("Object misses", v)) => {
                rec.object_misses = v
                    .parse()
                    .map_err(|_| ParseStatsError("Object misses".to_owned()))?
            }
            Some(("Object evictions", v)) => {
                rec.object_evictions = with_pct(v)
                    .map_err(|_| ParseStatsError("Object evictions".to_owned()))?
                    .1
            }
            _ => continue,
        }
    }
    Ok(rec)
}

fn with_pct(s: &str) -> nom::IResult<&str, (i32, f32)> {
    match separated_pair(
        digit1,
        tag(" "),
        delimited(tag("("), terminated(digit1, tag("%")), tag(")")),
    )(s)
    {
        Ok((i, (v, p))) => Ok((
            i,
            (v.parse().expect("v parse"), p.parse().expect("p parse")),
        )),
        Err(e) => Err(e),
    }
}
