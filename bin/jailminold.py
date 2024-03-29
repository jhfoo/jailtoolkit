#!/usr/local/bin/python3.8
# core modules
import os
import json
import traceback
import logging
# public modules
import requests
import yaml
# custom modules
import lib.util as util
import lib.clilib as cli
import lib.jailminlib as jailminlib
import lib.tasklib as tasklib
import lib.constant as c

def buildTemplate(opts):
  """Executes jail building"""
  BuildConfig = opts['BuildConfig']
  TemplateVars = opts['vars']

  # all vars replaced at this point
  if opts['DebugPath'] is not None:
    OutFile = open('{}BuildConfig.json'.format(opts['DebugPath']),'w')
    OutFile.write(json.dumps(BuildConfig, indent=2))
    OutFile.close()

    OutFile = open('{}vars.json'.format(opts['DebugPath']),'w')
    OutFile.write(json.dumps(TemplateVars, indent=2))
    OutFile.close()

  # print (json.dumps(BuildConfig, indent=2))

  jailminlib.destroyIfExist(BuildConfig['name'])

  # create jail
  util.execNWait('iocage create -r {} -n {}'.format(BuildConfig['release'], BuildConfig['name']))
  jailminlib.setProps(BuildConfig)

  installTemplate(opts)
  # # start jail
  # print ('Starting {}...'.format(BuildConfig['name']))
  # util.execNWait('iocage start {}'.format(BuildConfig['name']))

  # # install pkgs
  # if 'pkgs' in BuildConfig:
  #   jailminlib.installPkgs(BuildConfig['name'], BuildConfig['pkgs'])

  # # iterate through tasks
  # if 'tasks' in BuildConfig:
  #   tasklib.doTasks(opts)

  # util.execNWait('iocage set template=yes {}'.format(BuildConfig['name']))

def testGitGet(opts, fname):
  """Confirm code block necessary to GET raw GitHub private repo"""
  print (json.dumps(opts, indent=2))
  headers = {
    'Authorization': 'token {}'.format(opts['AppConfig']['github']['token']),
    'Accept': 'application/vnd.github.v3.raw'
  }
  url = 'https://raw.githubusercontent.com/{}/main/{}'.format(opts['AppConfig']['github']['RepoUrl'], fname)
  res = requests.get(url, headers=headers)
  if res.status_code == 200:
    print (res.text)
  else:
    print (res.text)

def installTemplate(opts):
  BuildConfig = opts['BuildConfig']
  JailInfo = jailminlib.getJailByName(BuildConfig['name'])
  if not JailInfo:
    raise Exception ('Jail does not exist: {}'.format(BuildConfig['name']))

  if JailInfo[c.JAILINFO_STATE] != c.JAILSTATE_UP: 
    # start jail
    print ('Start jail: {}'.format(BuildConfig['name']))
    util.execNWait('iocage start {}'.format(BuildConfig['name']))

  logger = logging.getLogger('default')
  logger.info ('Installing template: {}'.format(opts['TemplateName']))

  # install pkgs
  if 'pkgs' in BuildConfig:
    jailminlib.installPkgs(BuildConfig['name'], BuildConfig['pkgs'])

  # iterate through tasks
  if 'tasks' in BuildConfig:
    tasklib.doTasks(opts)

def execOptions(opts):
  """Executes main command"""
  logger = logging.getLogger('default')

  if opts['cmd'] == 'setprop':
    jailminlib.setProps(opts['TemplateName'])
    return

  if opts['cmd'] == c.CMD_BUILD:
    template = opts['BuildConfig']
    MandatoryKeys = [c.KEY_RELEASE]
    for key in MandatoryKeys:
      if key not in template:
        raise Exception ('Missing key \'{}\' in template'.format(key))

    logger.info ('Building {}...'.format(opts['TemplateName']))
    buildTemplate(opts)
    return

  if opts['cmd'] == c.CMD_INSTALL:
    installTemplate(opts)

  if opts['cmd'] == c.CMD_TEST:
    logger.info(json.dumps(opts, sort_keys=True, indent=2))
    # testGitGet(opts,'test.yaml')

try:
  print ('Script path: {}'.format(os.path.abspath(__file__)))
  ParsedOpts = cli.parseOptions()
  execOptions(ParsedOpts)
except Exception as e:
  logger = logging.getLogger('default')
  logger.error(traceback.format_exc())
  # print (e)
