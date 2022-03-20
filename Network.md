# Default Network Configuration
## Jails run in an isolated virtual network
1. Jails operate in a subnet orthogonal to the host network. 
2. ```vnet``` is the default interface.
3. Default bridge name is ```jailprivate```.

## IP address is immaterial
1. Jails are assigned IPs over DHCP.
2. The first jail to install should be the DHCP service used exclusively within the jail subnet.
3. Jails are referenced via FQDN as managed by Consul.

## Network routing options
Jails access services outside their subnet in either configuration:
1. Transparent networking: jail host and networks recognize the jail subnet, and are able to route bi-directionally.
2. NAT networking: jails access networks outside their subnet by impersonating the host address. If jails offer services consumed by clients outside their subnet the jail host exposes these services via port redirect (RDR in pf parlance).  