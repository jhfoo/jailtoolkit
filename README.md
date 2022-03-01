# jailmin (ALPHA)
Opinionated toolkit extending iocage to manage jail deployment.

## Pages
1. [Concepts](Concepts.md)
2. [Requirements & Assumptions](Assumptions.md)
3. [Examples](Examples.md)

## Goal
Combine basic jail management with modern jail management leveraging freely available utilities eg. iocage, Consul.

## Implementation
1. Priority towards jail management in a vnet network.
2. Support generic and extendable service configuration via 'templates'.

## Status
### Works
1. Package installer (installpkgs)
2. Network 'installer' (installnet)
2. Spinning up templated jails works though environment config is not well documented.

### In progress
2. Network installer (installnet) based on config in /usr/local/etc/jailmin.yaml



## Install
### Install dependency packages
~~~sh
git clone https://github.com/jhfoo/jailtoolkit.git
cd jailtoolkit
sudo ./bin/jailmin installpkgs
~~~
NOTE
1. Includes iocage

### Configure network
1. Sets up network used in jails.
2. Follows config in ```/usr/localetc/jailmin.yaml```.
~~~sh
sudo ./bin/jailmin installnet
~~~
NOTE
1. Updates /etc/rc.conf



## Command-line commands and options
- build
- -v: variable folder
- -i: ip4 address
- -n: jail name
- -c: app config file

