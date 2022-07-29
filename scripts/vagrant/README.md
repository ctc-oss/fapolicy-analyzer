# Vagrant config for demonstrating fapolicy analyzer

Nothing special, `vagrant up`

The default provisioning will be done from the [demo playbook](../demo)

### notes
- for virtualbox playbook support you will need ansible installed
  - `pip install -r requirements.txt`
- for virtualbox install you will need the vagrant plugin for the guest additions
  - `vagrant plugin install vagrant-vbguest`
- if using virtualbox and the guest additions keep reinstalled on every restart update plugins
  - `vagrant plugin update` 
