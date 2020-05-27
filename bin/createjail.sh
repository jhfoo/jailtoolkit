SIOCAGE='sudo iocage'
$SIOCAGE create -r 12.1-RELEASE -n $1
$SIOCAGE set bpf=1 $1
$SIOCAGE set vnet=1 $1
$SIOCAGE set dhcp=1 $1
$SIOCAGE start $1

# install pkgs
$SIOCAGE exec $1 "pkg install -y zsh git"

# create app account
$SIOCAGE exec $1 "echo abcdef | pw useradd app -h 0 -m"
$SIOCAGE exec $1 "touch /home/app/.zshrc"
