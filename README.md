# jailmin (DEPRECATED)
THIS REPO HAS BEEN A COLLECTION OF EXPERIMENTAL CODE TO ADD ADDITIONAL CAPABILITIES TO IOCAGE. PLEASE REFER TO [JAILMIN](https://github.com/jhfoo/jailtoolkit) AS THE SUCCESSOR REPO.

Opinionated toolkit extending iocage to manage jail deployment.

## Pages
1. [Concepts](Concepts.md)
2. [Requirements & Assumptions](Assumptions.md)
3. [Default network](Network.md)
4. [Examples](Examples.md)

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
1. Includes FreeBSD packages (iocage) and python libraries.

### Configure network
1. Sets up network used in jails.
2. Follows config in ```/usr/localetc/jailmin.yaml```.
~~~sh
sudo ./bin/jailmin installnet
~~~
NOTE
1. Updates /etc/rc.conf

## Command-line commands and options
~~~
build <template>   Builds the jail
test <template>    Displays build configuration
installpkgs        installs required packages
installnet         installs opinionated network settings
-v <folder>        variable folder
-i <address>       ip4 address
-n <name>          jail name
-c                 app config file
~~~
