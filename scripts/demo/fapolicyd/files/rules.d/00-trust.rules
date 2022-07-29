# Demonstration Rules

### 1. root can open/exec anything trusted
allow perm=any uid=0 trust=1 : all

### 2. vagrant can open/exec anything trusted
allow perm=any uid=1000 trust=1 : all

### 3. anyone else can execute trusted programs with a log entry
allow_syslog perm=execute all : trust=1

### 4. deny execution for anything untrusted
deny_syslog perm=execute all : all
