# This is the first non-core library loaded. It cannot include public-domain libraries
# core modules
from ctypes import util
import os
import sys
# custom modules
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
  pkgs = ['py38-iocage', 'py38-yaml']
  for pkg in pkgs:
    util.execNWait('pkg install -y {}'.format(pkg), isPrintRealtime = False)
