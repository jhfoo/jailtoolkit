[Home](README.md)
# Examples
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