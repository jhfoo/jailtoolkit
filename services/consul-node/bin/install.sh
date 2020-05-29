install()
{
  siocage="sudo iocage"
  $siocage exec $1 "git clone https://github.com/jhfoo/jailtoolkit.git"
  # jail to exec install script
  $siocage exec $1 "./jailtoolkit/services/consul-node/bin/localinstall.sh"
}

if [ -z "$1" ]
then
  echo ERROR: Missing argument for jail template
else
  install
fi

