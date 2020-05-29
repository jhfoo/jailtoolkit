INSTALL_BASEDIR=~/jailtoolkit
INSTALL_DIR=~/jailtoolkit/services/consul-node
CONSUL_CONF_DIR=/usr/local/etc/consul.d
export HOSTNAME=`hostname -s`

# If consul is already installed and running
service consul stop

# Remove existing config
rm $CONSUL_CONF_DIR/*

echo *** Installing consul pkg ***
pkg install -y consul perl5

echo *** Deploying basic config ***
# create conf dir
mkdir ${CONSUL_CONF_DIR}
chown consul:consul ${CONSUL_CONF_DIR}

# install templated configs
TEMPLATE_REPLACE="perl -pe 's;(\\*)(\$([a-zA-Z_][a-zA-Z_0-9]*)|\$\{([a-zA-Z_][a-zA-Z_0-9]*)\})?;substr($1,0,int(length($1)/2)).($2&&length($1)%2?$2:$ENV{$3||$4});eg'"
TARGET="${INSTALL_DIR}/conf/node.json.template"
DEST="${CONSUL_CONF_DIR}/node.json"
#$TEMPLATE_REPLACE $TARGET 
perl -pe 's;(\\*)(\$([a-zA-Z_][a-zA-Z_0-9]*)|\$\{([a-zA-Z_][a-zA-Z_0-9]*)\})?;substr($1,0,int(length($1)/2)).($2&&length($1)%2?$2:$ENV{$3||$4});eg' $TARGET > $DEST
rm $TARGET

TARGET="${INSTALL_DIR}/conf/"*
cp $TARGET $CONSUL_CONF_DIR

# Enable Consul to log in /var/log/consul
mkdir -p /var/log/consul
chown consul:consul /var/log/consul

# install custom config if specified
if [ -n "$1" ]
then
  cp "${INSTALL_BASEDIR}/jails/$1/conf/consul-"* "${CONSUL_CONF_DIR}/"
fi

# Start it up!
sysrc consul_enable="YES"
service consul start
