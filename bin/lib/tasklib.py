# core modules
import os
import sys
import re
import copy
import json
import logging
# custom modules
import lib.util as util
import lib.jailminlib as jailminlib
import lib.constant as c

def stringify4Template(value):
  if (type(value) == bool):
    return 1 if (value == True) else 0
  if (type(value) == int):
    return str(value)
  if (type(value) == str):
    return value

  # else: unexpected type
  raise Exception('Unhandled value type: {}'.format(type(value)))

def taskCopy(opts, task, WorkingPath):
  logger = logging.getLogger('default')

  if ('ApplyVars' in task and task['ApplyVars'] == True):
    # apply vars to text file
    print (task['src'])
    print (task['dest'])

    RawData = jailminlib.smartGetFile(opts['AppConfig'], task['src'], '{}', '')
    # InFile = open(task['src'],'r')
    # RawData = InFile.read()
    # InFile.close()

    vars = opts['vars']['vars']
    # replace vars in copy template
    for key in vars.keys():
      logger.info ('Replacing key {}'.format(key))
      RawData = RawData.replace('{{' + key + '}}', stringify4Template(vars[key]))

    # validate no unreplaced vars
    isMissingVars = False
    for key in re.findall('{{[A-Za-z]+}}', RawData):
      VarName = key[2:-2]
      isMissingVars = True
      logger.error ('ERROR: Variable {} not replaced'.format(VarName))
    if isMissingVars:
      sys.exit(1)

    TempFile = WorkingPath + os.path.basename(task['dest'])
    logger.info ('dest basename: {}'.format(os.path.basename(task['dest'])))
    OutFile = open(TempFile,'w')
    OutFile.write(RawData)
    OutFile.close()

    util.execNWait('cp {} {}'.format(TempFile, task['dest']))
    # housekeeping
    os.remove(TempFile)
  else:
    # binary copy
    util.execNWait('cp {} {}'.format(task['src'], task['dest']))

def smartTemplateRoot(TemplatePath, TemplateName, PathFormat):
  if TemplateName.startswith('github'):
    return PathFormat.format('github:', TemplateName[7:])
  # else
  return PathFormat.format(TemplatePath, TemplateName)

def taskRunTemplate(opts, task):
  TaskOpts = copy.deepcopy(opts)
  TaskOpts['ValidateTemplate'] = False
  TaskOpts['JailName'] = opts['BuildConfig']['name']
  TaskOpts['TemplateName'] = task['template']
  TaskOpts['vars']['vars']['TEMPLATEROOT'] = smartTemplateRoot(opts['TemplatePath'], TaskOpts['TemplateName'], '{}/templates/{}/')
  # TaskOpts['vars']['vars']['TEMPLATEROOT'] = '{}/templates/{}/'.format(opts['TemplatePath'], TaskOpts['TemplateName'])
  TaskOpts['BuildConfig'] = jailminlib.getMergedTemplate(TaskOpts)

  if (opts['DebugPath'] != None):
    OutFile = open('{}{}-BuildConfig.json'.format(TaskOpts['DebugPath'], task['template']),'w')
    OutFile.write(json.dumps(TaskOpts, indent=2))
    OutFile.close()

  # install pkgs
  BuildConfig = TaskOpts['BuildConfig']
  if 'pkgs' in BuildConfig:
    jailminlib.installPkgs(BuildConfig['name'], BuildConfig['pkgs'])

  # iterate through tasks
  if ('tasks' in BuildConfig):
    doTasks(TaskOpts)

def doTasks(opts):
  logger = logging.getLogger('default')

  BuildConfig = opts['BuildConfig']
  vars = opts['vars']

  for task in BuildConfig['tasks']:
    logger.info ('TASK: {}'.format(task[c.KEY_NAME]))
    if (task['do'] == c.TASK_JAILEXEC):
      util.execNWait('iocage exec {} "{}"'.format(BuildConfig['name'], task['cmd']))
      continue
    if (task['do'] == c.TASK_JAILRESTART):
      util.execNWait('iocage restart {}'.format(BuildConfig['name']))
      continue
    if (task['do'] == c.TASK_COPY):
      taskCopy(opts, task, opts['WorkingPath'])
      continue
    if (task['do'] == c.TASK_RUNTEMPLATE):
      taskRunTemplate(opts, task)
      continue
