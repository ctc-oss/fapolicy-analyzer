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

## Use a GitHub release tag
```
analyzer_version=v0.5.3 vagrant up --provision
```

if `analyzer_version` is not specified the latest release will be used (non-prerelease)

## Use a locally built RPM
```
vagrant scp my.rpm /tmp
vagrant ssh
sudo yum install /tmp/my.rpm
```
