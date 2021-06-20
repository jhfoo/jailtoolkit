# jailtoolkit (WIP)
Toolkit to manage jail deployment with applications

## Goal
A set of scripts and configuration to help FreeBSD administrators automate application deployment in jails with 'sidecar' apps like Consul to manage them collectively.

## Implementation
Heavy dependency on iocage and Python.

## Requirements (tested)
- [FreeBSD 12.2 (RELEASE)](https://www.freebsd.org/where.html)
- [Python 3.7](https://docs.python.org/3.7/)
- [Iocage 1.2](https://github.com/iocage/iocage)
- [Consul 1.9.1](https://www.consul.io/)

## Usage
To be used on a non-root account with sudo capabilities (wheel group?)

## Assumptions
- Zsh default shell on account
- User has root or sudo access

## Install
~~~sh
git clone https://github.com/jhfoo/jailtoolkit.git
cd jailtoolkit/bin
./install.sh
# install dependencies
# assumes Python 3.7 installed
sudo pkg install -y py37-yaml
~~~

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