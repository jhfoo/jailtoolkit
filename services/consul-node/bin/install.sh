if [ $# -eq 0 ]
then
  echo "[consul-node] ERROR: Missing argument for jail temp.late"
  echo "[consul-node] Usage: install.sh <JailId> <arguments>"
else
  siocage="sudo iocage"
  $siocage exec $1 "rm -rf ~/jailtoolkit"
  $siocage exec $1 "cd ~ && git clone https://github.com/jhfoo/jailtoolkit.git"
  # jail to exec install script
  $siocage exec $1 "~/jailtoolkit/services/consul-node/bin/localinstall.sh $2"
fi

