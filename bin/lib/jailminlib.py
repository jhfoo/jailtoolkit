# core modules
import os
import sys
import re
# custom modules
import lib.util as util

AppBasePath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
TemplatePath = '/usr/local/etc/jailmin/' if (AppBasePath.startswith('/usr/local/bin/')) else os.path.abspath('./')

def getTemplates(isTemplate = True):
  templates = []
  # switch between templates and jails
  TempString = '-t' if (isTemplate == True) else ''
  ExecResult = util.execNWait('iocage list {}'.format(TempString), isPrintRealtime = False)
  if (ExecResult['ExitCode'] == 0):
    lines = ExecResult['output'].split('\n')
    if (len(lines) > 3):
      lines.pop(0)
      lines.pop(0)
      lines.pop(0)

    for line in lines:
      columns = line.split('|')
      if (len(columns) == 7):
        fields = {
          'jid': columns[1].strip(),
          'name': columns[2].strip(),
          'state': columns[3].strip(),
          'release': columns[4].strip(),
          'address': columns[5].strip(),
        }
        templates.append(fields)

  return templates

def getPropValue(value):
  if (type(value) is bool):
    return 1 if (value == True) else 0
  # if (type(value) is str):
  return '"{}"'.format(value)

def getJailProps(JailName):
  RawJailProps = util.execNWait('iocage get all {}'.format(JailName), isPrintRealtime = False, isContinueOnError = True)
  if (RawJailProps['ExitCode'] != 0):
    # jail does not exist
    return None

  props = {}
  for line in RawJailProps['output'].split('\n'):
    columns = line.split(':')
    if (len(columns) > 1):
      props[columns[0]] = columns[1]
  return props

def getVars(opts):
  # load default vars
  DefaultVars = util.readYamlFile(opts['TemplatePath'] + '/jails/default/vars.yaml')

  VarFile = None 
  if ('VarFile' in opts):
    VarFile = opts['TemplatePath'] + '/jails/' + opts['VarFile'] + '/vars.yaml'
  if (VarFile == None):
    return DefaultVars

  # load custom vars
  CustomVars = util.readYamlFile(VarFile)

  # custom vars override defaults
  CustomVarsKeys = CustomVars['vars'].keys()
  for key in DefaultVars['vars'].keys():
    if (key not in CustomVarsKeys):
      CustomVars['vars'][key] = DefaultVars['vars'][key]

  return CustomVars

def getMergedTemplate(opts):
  VarDict = opts['vars']
  vars = VarDict['vars'] if ('vars' in VarDict.keys()) else {}
  template = util.readYamlFile(TemplatePath + '/templates/' + opts['TemplateName'] + '/template.yaml', vars)

  # props in VarFile overrides template defaults
  if 'props' in VarDict.keys():
    if 'props' not in template:
      template['props'] = {}
    for key in VarDict['props'].keys():
      template['props'][key] = VarDict['props'][key]

  # support command-line jail naming
  if 'JailName' in opts:
    template['name'] = opts['JailName']

  # post-merge var processing
  # iterate config selectively: light pass through tasks
  DefaultVars = {
    'JAILROOT': '/zroot/iocage/jails/{}/root/'.format(template['name']),
    'TEMPLATEROOT': '{}/templates/{}/'.format(TemplatePath, opts['TemplateName']),
    'JAILNAME': template['name']
  }

  # update vars so nested templates can substitute early
  for key in DefaultVars.keys():
    vars[key] = DefaultVars[key]

  if 'tasks' in template:
    for task in template['tasks']:
      for key in task.keys():
        if (type(task[key]) is str):
          for VarName in re.findall('\$\$[A-Za-z]+\$\$', task[key]):
            KeyInTask = VarName[2:-2]
            if KeyInTask in DefaultVars:
              task[key] = task[key].replace(VarName, DefaultVars[KeyInTask])
            else:
              raise Exception('Missing variable {}'.format(KeyInTask))

  # light template validation
  if ('ValidateTemplate' not in opts or opts['ValidateTemplate'] == True):
    MandatoryKeys = ['name','release']
    for key in MandatoryKeys:
      if key not in template:
        raise Exception ('Missing key {} in template'.format(key))

  return template

def setProps(BuildConfig):
  props = getJailProps(BuildConfig['name'])

  # stop jail if running
  if (props != None and props['state'] == 'up'):
    print ('{} is running: stopping'.format(BuildConfig['name']))
    util.execNWait('iocage stop {}'.format(BuildConfig['name']))

  for key in BuildConfig['props'].keys():
    print ('{} = {}'.format(key, getPropValue(BuildConfig['props'][key])))
    util.execNWait('iocage set {}={} {}'.format(key, getPropValue(BuildConfig['props'][key]), BuildConfig['name']), isContinueOnError=True)

def destroyIfExist(TemplateName):
  templates = getTemplates(False)
  for temp in templates:
    if temp['name'] == TemplateName:
      util.execNWait('iocage destroy -f {}'.format(TemplateName))
      return True
  
  # nothing destroyed
  return False

def installPkgs(JailName, PkgList):
  PkgStr = ' '.join(PkgList)
  print ('Installing pkgs: {}'.format(PkgStr))
  util.execNWait('iocage exec {} "{}"'.format(JailName, 'pkg install -y {}'.format(PkgStr)))

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
