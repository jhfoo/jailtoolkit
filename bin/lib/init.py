# This is the first non-core library loaded. It cannot include public-domain libraries
# core modules
# from ctypes import util
# from fileinput import close
from curses import has_key
import os
import sys
import re
import yaml
# custom modules
import lib.logger as logger
import lib.constant as c
import lib.coreutil as util

def validateRoot():
  """Confirms process has root privileges"""
  if os.getuid() != 0:
    print ('INSUFFICIENT PRIVILEGES: jailmin requires root privileges to run some commmands (eg. iocage). Run jail as root or use sudo')
    sys.exit(1)

def quickParseOptions():
  """Processes command-line arguments"""
  if len(sys.argv) < 2:
    print ('Usage: jailmin [{}|{}|{}|{}|{}] template [params]'.format(c.CMD_TEST, c.CMD_INSTALL, c.CMD_BUILD, c.CMD_INITNET, c.CMD_INSTALLPKGS, c.CMDPARAM_JAILNAME))
    print ("""Params: 
  {}\tip address
  {}\tvarfile
  {}\tjailname""".format(c.CMDPARAM_IPADDR, c.CMDPARAM_VARFILE, c.CMDPARAM_JAILNAME))
    sys.exit(0)

def installPkgs():
  """Install Python packages"""
  logger.info('installPkgs():')
  pkgs = ['py38-iocage', 'py38-yaml']
  for pkg in pkgs:
    logger.info('pkg install: {}'.format(pkg))
    util.execNWait('pkg install -y {}'.format(pkg), isPrintRealtime = False)

def readRcConf():
  """Parse /etc/rc.conf into key-value dict"""
  ret = {}
  InFile = open('/etc/rc.conf', 'r')
  for line in InFile.readlines():
    if re.match('^\s*#', line) == None:
      result = re.match('^\s*(.+?)\s*=\s*(.+)$', line.strip())
      if result != None:
        MatchQuotes = re.match('^"(.*)"$', result.group(2))
        value = result.group(2) if MatchQuotes == None else MatchQuotes.group(1).strip()
        ret[result.group(1)] = value
  InFile.close()

  return ret

def readJailminYaml():
  InFile = open('/usr/local/etc/jailmin.yaml', 'r')
  doc = yaml.load(InFile.read(), Loader=yaml.FullLoader)
  InFile.close()

  return doc

def setRcConfig(config, key, value):
  if key in config.keys():
    if config[key] == value:
      return

  print ('sysrc {}="{}"'.format(key, value))
  util.execNWait('sysrc {}="{}"'.format(key, value))

def installNet():
  """Configure jail network settings"""
  logger.info('installNet():')
  RcConfig = readRcConf()
  JailminConfig = readJailminYaml()
  print (RcConfig)
  print (JailminConfig)
  setRcConfig(RcConfig, 'gateway_enable', 'YES')