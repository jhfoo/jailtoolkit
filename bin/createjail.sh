BASEDIR=~/jailtoolkit

# load configurable params
. $BASEDIR/conf/createjail.conf

# parse options
OPT_NOBRIDGE=0

while [ -n "$1" ]
do
  case "$1" in
  -nobridge)
    echo "[Option] Remove $IF_HOST from bridge $IF_BRIDGE"
    OPT_NOBRIDGE=1
    shift ;;
  -y)
    echo "-y"
    shift ;;
  *)
    break ;;
  esac
done

SIOCAGE='sudo iocage'
$SIOCAGE create -r $JAIL_RELEASE -n $1
$SIOCAGE set bpf=1 $1
$SIOCAGE set vnet=1 $1
$SIOCAGE set dhcp=1 $1

if [ $OPT_NOBRIDGE -eq 1 ]
then 
  echo Removing host interface from bridge
  sudo ifconfig $IF_BRIDGE deletem $IF_HOST
fi

$SIOCAGE start $1

# install pkgs
$SIOCAGE exec $1 "pkg install -y ${INSTALL_PACKAGES}"

# create app account
$SIOCAGE exec $1 "echo ${APP_PWD} | pw useradd ${APP_ID} -h 0 -m -s /usr/local/bin/zsh"
$SIOCAGE exec $1 "touch /home/${APP_ID}/.zshrc"
