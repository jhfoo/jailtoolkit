pkg install openjdk13

BIN_SRC="https://download.gocd.org/binaries/20.4.0-11749/generic/go-server-20.4.0-11749.zip"
APP_BASEDIR=~/jailtoolkit/services/gocd-server

mkdir -p ${APP_BASEDIR}/tmp
DEST_FILE=$APP_BASEDIR/tmp/server.zip
if [ ! -f $DEST_FILE ]
then
  curl $BIN_SRC --output $DEST_FILE
fi

USERACCT_BASEDIR=/home/app
rm -rf $USERACCT_BASDIR/go-server*
tar -C $USERACCT_BASEDIR -xvf $DEST_FILE
mv "$USERACCT_BASEDIR/go-server"* $USERACCT_BASEDIR/go-server

$USERACCT_BASEDIR/go-server/bin/go-server start
