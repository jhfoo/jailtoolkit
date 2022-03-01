[Home](README.md)
# Jailmin Concepts

## Templates
1. Templates are YAML files describing how a jail is to be set up
2. Templates can be nested (eg. load sidecars such as Consul or install services such Nginx) 

## Variables
1. Variables are custom configurable specific to the user's setup (eg. jail properties), to be applied on templates.

## Tasks
1. Tasks describe actions necessary to set up a service (eg. Consul).
2. Valids commands
 - jailrestart: restart jail
 - jailexec: run a command as root in jail
 - copy: supports templates and variables
 - runtemplate

## Notes
### Configuring bridges
1. If you're using vtnet, remember to enable promiscuous mode (promisc, [bug](https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=254343)) or it cannot be added to the bridge:
```
ifconfig_vtnet0="inet 192.168.0.20/24 promisc"
```