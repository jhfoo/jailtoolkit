BASEDIR=~/jailtoolkit
. $BASEDIR/conf/createjail.conf

SIOCAGE='sudo iocage'
$SIOCAGE create -r $JAIL_RELEASE -n $1
$SIOCAGE set bpf=1 $1
$SIOCAGE set vnet=1 $1
$SIOCAGE set dhcp=1 $1
$SIOCAGE start $1

# install pkgs
$SIOCAGE exec $1 "pkg install -y ${INSTALL_PACKAGES}"

# create app account
$SIOCAGE exec $1 "echo ${APP_PWD} | pw useradd ${APP_ID} -h 0 -m -s /usr/local/bin/zsh"
$SIOCAGE exec $1 "touch /home/${APP_ID}/.zshrc"
