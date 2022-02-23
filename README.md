# jailmin (ALPHA)
Opinionated toolkit extending iocage to manage jail deployment.

## Goal
Combine basic jail management with modern jail management leveraging freely available utilities eg. iocage, Consul.

## Implementation
1. Priority towards jail management in a vnet network.
2. Support generic and extendable service configuration via 'templates'.

## Status
### Works
1. Package installer (installpkgs)
2. Spinning up templated jails works though environment config is not well documented.

### In progress
2. Network installer (installnet) based on config in /usr/local/etc/jailmin.yaml

## Requirements (tested)
- Softwares
  - [FreeBSD 13.0 (RELEASE)](https://www.freebsd.org/where.html)
  - [Python 3.8](https://docs.python.org/3.8/)
  - [Iocage 1.2](https://github.com/iocage/iocage)
  - [Consul 1.9](https://www.consul.io/)
- Permissions
  - Root or sudo-able account

## Assumptions
- Zsh default shell on account

## Install
### Install dependency packages
~~~sh
git clone https://github.com/jhfoo/jailtoolkit.git
cd jailtoolkit
sudo ./bin/jailmin installpkgs
~~~
NOTE: Includes iocage

### Configure network
~~~sh
sudo ./bin/jailmin installnet
~~~
NOTE: Updates /etc/rc.conf

## Examples
Create a simple jail with static ip
~~~ sh
# pwd: jailtoolkit/
# jail hostname = hellojail
# TODO: set ip below to a valid address
./bin/jailmin build basic -n hellojail -i 192.168.0.58/24
~~~

Create a simple jail with static ip and Nginx
~~~ sh
# pwd: jailtoolkit/
# jail hostname = hellojail
# TODO: set ip below to a valid address
./bin/jailmin build basicnginx -n hellojail -i 192.168.0.58/24
~~~

Create a simple jail with static ip from config in GitHub
~~~ sh
# pwd: jailtoolkit/
# jail hostname = hellojail
# TODO: set ip below to a valid address
./bin/jailmin build github:basic -n hellojail -i 192.168.0.58/24
~~~

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

## Command-line commands and options
- build
- -v: variable folder
- -i: ip4 address
- -n: jail name
- -c: app config file