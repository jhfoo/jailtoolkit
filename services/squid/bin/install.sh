if [ $# -eq 0 ]
then
  echo "[squid] Missing parameters"
  echo "[squid] Usage: install.sh <JailId>"
  exit 1
fi

SIOCAGE="sudo iocage exec $1"
$SIOCAGE pkg install -y squid ca_root_nss
$SIOCAGE sysrc squid_enable="YES"
$SIOCAGE service squid -z -N
$SIOCAGE -R squid:squid /var/squid/cache
$SIOCAGE service squid start
