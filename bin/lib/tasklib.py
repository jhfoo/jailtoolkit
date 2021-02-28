# core modules
import os
import sys
import re
import copy
import json
# custom modules
import lib.util as util
import lib.jailminlib as jailminlib

def stringify4Template(value):
  if (type(value) == bool):
    return 1 if (value == True) else 0
  if (type(value) == int):
    return str(value)
  if (type(value) == str):
    return value

  # else: unexpected type
  raise Exception('Unhandled value type: {}'.format(type(value)))

def taskCopy(vars, task, WorkingPath):
  if ('ApplyVars' in task and task['ApplyVars'] == True):
    # apply vars to text file
    print (task['src'])
    print (task['dest'])

    InFile = open(task['src'],'r')
    RawData = InFile.read()
    InFile.close()

    # replace vars in copy template
    for key in vars.keys():
      print ('Replacing key {}'.format(key))
      RawData = RawData.replace('{{' + key + '}}', stringify4Template(vars[key]))

    # validate no unreplaced vars
    isMissingVars = False
    for key in re.findall('{{[A-Za-z]+}}', RawData):
      VarName = key[2:-2]
      isMissingVars = True
      print ('ERROR: Variable {} not replaced'.format(VarName))
    if isMissingVars:
      sys.exit(1)

    TempFile = WorkingPath + os.path.basename(task['dest'])
    print ('dest basename: {}'.format(os.path.basename(task['dest'])))
    OutFile = open(TempFile,'w')
    OutFile.write(RawData)
    OutFile.close()

    util.execNWait('cp {} {}'.format(TempFile, task['dest']))
    # housekeeping
    os.remove(TempFile)
  else:
    # binary copy
    util.execNWait('cp {} {}'.format(task['src'], task['dest']))

def taskRunTemplate(opts, task):
  TaskOpts = copy.deepcopy(opts)
  TaskOpts['ValidateTemplate'] = False
  TaskOpts['JailName'] = opts['BuildConfig']['name']
  TaskOpts['TemplateName'] = task['template']
  TaskOpts['vars']['vars']['TEMPLATEROOT'] = '{}/templates/{}/'.format(opts['TemplatePath'], TaskOpts['TemplateName'])
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
  BuildConfig = opts['BuildConfig']
  vars = opts['vars']

  for task in BuildConfig['tasks']:
    print ('TASK: {}'.format(task['name']))
    if (task['do'] == 'jailexec'):
      util.execNWait('iocage exec {} "{}"'.format(BuildConfig['name'], task['cmd']))
      continue
    if (task['do'] == 'jailrestart'):
      util.execNWait('iocage restart {}'.format(BuildConfig['name']))
      continue
    if (task['do'] == 'copy'):
      taskCopy(vars['vars'], task, opts['WorkingPath'])
      continue
    if (task['do'] == 'runtemplate'):
      taskRunTemplate(opts, task)
      continue
