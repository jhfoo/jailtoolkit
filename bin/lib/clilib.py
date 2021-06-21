# core modules
import os
import sys
import shutil
# public modules
import getpass
import yaml
# custom modules
import lib.constant as c
import lib.jailminlib as jailminlib

def validateRoot():
  """Confirms process has root privileges"""
  if getpass.getuser() != 'root':
    print ('INSUFFICIENT PRIVILEGES: jailmin requires root privileges to run some commmands (eg. iocage). Run jail as root or use sudo')
    sys.exit(1)

def readConfig(AltAppConfigFile):
  """Read/ parse jailmin config"""
  FILE_APPCONFIG = '/usr/local/etc/jailmin.yaml'

  AppConfigFile = FILE_APPCONFIG if AltAppConfigFile is None else AltAppConfigFile
  if os.path.exists(AppConfigFile):
    InFile = open(AppConfigFile)
    config = yaml.load(InFile.read(), Loader=yaml.FullLoader)
    InFile.close()
    return config
  # else
  raise Exception('Missing app config: {}'.format(AppConfigFile))

def parseOptions():
  """Processes command-line arguments"""
  if len(sys.argv) < 2:
    print ('Usage: jailmin [{}|{}|{}] template [params]'.format(c.CMD_TEST, c.CMD_INSTALL, c.CMD_BUILD, c.CMDPARAM_JAILNAME))
    print ("""Params: 
  {}\tip address
  {}\tvarfile
  {}\tjailname""".format(c.CMDPARAM_IPADDR, c.CMDPARAM_VARFILE, c.CMDPARAM_JAILNAME))
    sys.exit(0)

  AppBasePath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
  opts = {
    'TemplatePath': '/usr/local/etc/jailmin/' if (AppBasePath.startswith('/usr/local/bin/')) else os.path.abspath('./'),
    'DebugPath': '{}/'.format(os.path.abspath('./debug')),
    'WorkingPath': '{}/'.format(os.path.abspath('./temp'))
  }
  # work on a copy of argv
  args = sys.argv.copy()
  args.pop(0)

  while len(args) > 0:
    param = args.pop(0)
    # if param == 'install':
    #   print ('WARNING: You must be root or running-as root to install to /usr/local/bin')
    #   shutil.copyfile(os.path.abspath(__file__), '/usr/local/bin/jailmin')
    #   print ('jailmin installed')
    #   continue
    if param == 'setprop':
      opts['cmd'] = param
      opts['TemplateName'] = args.pop(0)
      continue
    if param == c.CMD_INSTALL:
      opts['cmd'] = param
      opts['TemplateName'] = args.pop(0)
      continue
    if param == c.CMD_TEST:
      opts['cmd'] = param
      opts['TemplateName'] = args.pop(0)
      continue
    if param == c.CMD_BUILD:
      opts['cmd'] = param
      opts['TemplateName'] = args.pop(0)
      continue
    if param == c.CMDPARAM_IPADDR:
      opts['Ip4Addr'] = args.pop(0)
      continue
    if param == '-c':
      opts['AppFile'] = args.pop(0)
      continue
    if param == c.CMDPARAM_VARFILE:
      opts['VarFile'] = args.pop(0)
      continue
    if param == '-d':
      print (os.path.abspath(args.pop(0)))
      # opts['DebugPath'] = args.pop(0)
      continue
    if param == c.CMDPARAM_JAILNAME:
      opts['JailName'] = args.pop(0)
    else:
      print ('ERROR: Unexpected param {}'.format(param))
      sys.exit(2)

  opts['AppConfig'] = readConfig(opts['AppFile'] if 'AppFile' in opts else None)

  if 'cmd' in opts:
  # if 'cmd' in opts and opts['cmd'] != 'test':
    opts['vars'] = jailminlib.getVars(opts)
    opts['BuildConfig'] = jailminlib.getMergedTemplate(opts)
  return opts