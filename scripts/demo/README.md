# Scripting a demonstration of the system with Vagrant and Ansible.

This playbook is wired into the [vagrant fc34 directory](../vagrant/fc34) to set up a demonstration environment.

The following commands were used to develop the playbook and initial demonstration.

## Up and provision
```
vagrant up
```

## Reprovision (just change the playbook)
```
vagrant up --provision
```

## Use a GitHub release RPM
```
export rpm_url='https://github.com/ctc-oss/fapolicy-analyzer/releases/download/v0.3.0-rc02108301/fapolicy-analyzer-0.3.0-0.rc02108301.fc34.x86_64.rpm'
vagrant up --provision
```

## Use a locally built RPM
```
vagrant scp my.rpm /tmp
vagrant ssh
sudo yum install /tmp/my.rpm
```
