# jailtoolkit (WIP)
Toolkit to manage jail deployment with applications

## Goal
A set of scripts and configuration to assist FreeBSD administrators to automate application deployment in jails with 'sidecar' apps like Consul to manage them collectively.

## Implementation
Heavy dependency on iocage and Python.

## Requirements
- [FreeBSD 12.1 (RELEASE)](https://www.freebsd.org/where.html)
- Python 3.7
- [Iocage 1.2](https://github.com/iocage/iocage)
- [Consul 1.7](https://www.consul.io/)

## Usage
To be used on a non-root account with sudo capabilities (wheel group?)

## Assumptions
- Zsh default shell on account

## Install
~~~sh
git clone https://github.com/jhfoo/jailtoolkit.git
cd jailtoolkit/bin
./install.sh
~~~

## Key scripts
### bin/createjail.py
- Collates template configurations to create primarily a vnet, DHCP-based jail
- Run syntax
```
python bin/createjail.py jailname [-t jailtemplate] [-h hosttemplate] [-v varstemplate]
```
- Sample create
```
python bin/createjail.py jailname
```
- References files in 
  - conf/createjail-default.yaml
  - hosts/[hostname]/createjail-vars.yaml

### bin/createjail [jail name] - DEPRECATED
- Creates jail on DHCP
- Installs basic packages eg. Git
- Creates app account with Zsh shell
- Config at `conf/createjail.conf`

##### TODO
- Have a plan for app password
- Optionally run installconsul

### bin/installsvc [ServiceId] [arguments]
- Executes services/[ServiceId]/bin/install.sh [arguments]

## Services
- consul-node [JailId] [JailTemplateId]
