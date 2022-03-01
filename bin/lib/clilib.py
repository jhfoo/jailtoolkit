# core modules
import os
import sys
import shutil
import logging

# public modules
import yaml

# custom modules
import lib.constant as c
import lib.jailminlib as jailminlib

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
  AppBasePath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
  opts = {
    'TemplatePath': '/usr/local/etc/jailmin/' if (AppBasePath.startswith('/usr/local/bin/')) else os.path.abspath('./'),
    'DebugPath': '{}/'.format(os.path.abspath('./debug')),
    'WorkingPath': '{}/'.format(os.path.abspath('./temp'))
  }

  # create paths
  AutocreatePaths = ['WorkingPath', 'TemplatePath', 'DebugPath']
  for path in AutocreatePaths:
    if not os.path.exists(opts[path]):
      os.makedirs(opts[path])

  # set debug logger
  ConsoleOut = logging.StreamHandler()
  ConsoleOut.setLevel(logging.INFO)
  ConsoleOut.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

  OutFile = logging.FileHandler('{}/jailmin.log'.format(opts['DebugPath']))
  OutFile.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

  DefaultLogger = logging.getLogger('default')
  DefaultLogger.setLevel(logging.DEBUG)
  DefaultLogger.addHandler(OutFile)
  DefaultLogger.addHandler(ConsoleOut)
  DefaultLogger.debug('parseOptions: DebugPath set')
  
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
