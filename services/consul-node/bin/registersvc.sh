service consul stop
cp ~/jailtoolkit/jails/$1/conf/* /usr/local/etc/consul.d/
service consul start
