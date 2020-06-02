if [ $# -eq 0 ]
then
  echo "installservice.sh <ServiceId> <args>"
else
  SERVICE_BIN="./services/$1/bin/install.sh"
  shift
  $SERVICE_BIN $@
fi

