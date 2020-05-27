# jailtoolkit (WIP)
Toolkit to manage jail deployment with applications

## Goal
A set of scripts and configuration to assist FreeBSD administrators to autommate application deployment in jails with 'sidecar' apps like Consul to manage them collectively.

## Requirements
- [FreeBSD 12.1 (RELEASE)](https://www.freebsd.org/where.html)
- [Iocage](https://github.com/iocage/iocage)
- [Consul](https://www.consul.io/)

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

## Script: createjail [jail name]
- Creates jail on DHCP
- Installs basic packages eg. Git
- Creates app account with Zsh shell
- Config at `conf/createjail.conf`

### TODO
- ~~Make package list configurable~~
- Have a plan for app password
- Optionally run installconsul

## Service: Consul (node) [jail name]
- Installs Consul and dependent packages
- Script path: `services/consul-node/bin`
- Deploys basic Consul config

### TODO
- Make basic config more configurable
  - Extract configurable parameters into separate file
