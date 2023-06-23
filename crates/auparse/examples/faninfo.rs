use auparse_sys::event::Event;
use chrono::{DateTime, NaiveDateTime, Utc};
use fapolicy_auparse::error::Error;
use fapolicy_auparse::logs::Logs;
use fapolicy_auparse::record;
use fapolicy_auparse::record::Type::Fanotify;
use std::time::SystemTime;

#[derive(Debug)]
pub struct FanEvent {
    pub rule_id: i32,
    pub dec: String,
    pub perm: String,
    pub uid: i32,
    pub gid: Vec<i32>,
    pub pid: i32,
    pub subj: String,
    pub obj: String,
    pub when: Option<DateTime<Utc>>,
}

//type=PROCTITLE msg=audit(06/23/2023 03:37:44.624:8583) : proctitle=-bash
// type=PATH msg=audit(06/23/2023 03:37:44.624:8583) : item=0 name=/tmp/exec inode=2311 dev=00:2f mode=file,755 ouid=vagrant ogid=vagrant rdev=00:00 obj=unconfined_u:object_r:user_tmp_t:s0 nametype=NORMAL cap_fp=none cap_fi=none cap_fe=0 cap_fver=0 cap_frootid=0
// type=CWD msg=audit(06/23/2023 03:37:44.624:8583) : cwd=/home/vagrant
// type=SYSCALL msg=audit(06/23/2023 03:37:44.624:8583) : arch=x86_64 syscall=execve success=no exit=EPERM(Operation not permitted) a0=0x56294d1799d0 a1=0x56294d1bb300 a2=0x56294d181820 a3=0x8 items=1 ppid=118132 pid=118216 auid=vagrant uid=vagrant gid=vagrant euid=vagrant suid=vagrant fsuid=vagrant egid=vagrant sgid=vagrant fsgid=vagrant tty=pts0 ses=81 comm=bash exe=/usr/bin/bash subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 key=(null)
// type=FANOTIFY msg=audit(06/23/2023 03:37:44.624:8583) : resp=deny fan_type=rule_info fan_info=2 subj_trust=unknown obj_trust=no

//////////////////////////

// type=PROCTITLE msg=audit(06/13/2023 13:27:11.267:1224) : proctitle=tee /tmp/deny/foo
// type=PATH msg=audit(06/13/2023 13:27:11.267:1224) : item=1 name=/tmp/deny/foo inode=56 dev=00:2f mode=file,644 ouid=vagrant ogid=vagrant rdev=00:00 obj=unconfined_u:object_r:user_tmp_t:s0 nametype=NORMAL cap_fp=none cap_fi=none cap_fe=0 cap_fver=0 cap_frootid=0
// type=PATH msg=audit(06/13/2023 13:27:11.267:1224) : item=0 name=/tmp/deny/ inode=54 dev=00:2f mode=dir,755 ouid=vagrant ogid=vagrant rdev=00:00 obj=unconfined_u:object_r:user_tmp_t:s0 nametype=PARENT cap_fp=none cap_fi=none cap_fe=0 cap_fver=0 cap_frootid=0
// type=CWD msg=audit(06/13/2023 13:27:11.267:1224) : cwd=/home/vagrant
// type=SYSCALL msg=audit(06/13/2023 13:27:11.267:1224) : arch=x86_64 syscall=openat success=no exit=EPERM(Operation not permitted) a0=AT_FDCWD a1=0x7fff8f79d527 a2=O_WRONLY|O_CREAT|O_TRUNC a3=0x1b6 items=2 ppid=15940 pid=16046 auid=vagrant uid=vagrant gid=vagrant euid=vagrant suid=vagrant fsuid=vagrant egid=vagrant sgid=vagrant fsgid=vagrant tty=pts0 ses=25 comm=tee exe=/usr/bin/tee subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 key=(null)
// type=FANOTIFY msg=audit(06/13/2023 13:27:11.267:1224) : resp=deny fan_type=rule_info fan_info=4 subj_trust=unknown obj_trust=no
fn parse(e: Event) -> Option<FanEvent> {
    Some(FanEvent {
        rule_id: e.int("fan_info").expect("fan_info"),
        dec: e.str("resp").expect("resp"),
        uid: e.int("uid").expect("uid"),
        gid: vec![e.int("gid").expect("gid")],
        pid: e.int("pid").expect("pid"),
        subj: e.str("exe").expect("exe"),
        perm: "-".to_string(),
        obj: e.str("name").expect("name"),
        when: Some(DateTime::from_utc(
            NaiveDateTime::from_timestamp(e.ts(), 0),
            Utc,
        )),
    })
}

fn main() -> Result<(), Error> {
    Logs::filtered(parse, |x| x == Fanotify)?.for_each(|e| println!("{:?}", e));
    Ok(())
}
