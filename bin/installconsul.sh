siocage="sudo iocage"
$siocage exec $1 "git clone https://github.com/jhfoo/consulinstall.git"
$siocage exec $1 "./consulinstall/bin/install.sh"
