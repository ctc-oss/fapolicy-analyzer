# fapolicyd configuration can impact the accuracy of what fapolicy-analyzer reports

### Integrity controls what part of the trust database is used to validate the file integrity (none, size, sha256, ima)
integrity = size

### The logging format externalizes various required parts of the decision metadata to the analyzer
syslog_format = rule,dec,perm,uid,gid,pid,exe,:,path,ftype,trust

### Excluding volumes based on fs type would impact what files should be analyzed
watch_fs = ext2,ext3,ext4,tmpfs,xfs,vfat,iso9660

### The system trust store or the ancillary could be switched off
trust = rpmdb,file

## other standard settings
permissive = 0  
nice_val = 14  
q_size = 640  
uid = fapolicyd  
gid = fapolicyd  
do_stat_report = 1  
detailed_report = 1  
db_max_size = 40  
subj_cache_size = 1549  
obj_cache_size = 8191  
