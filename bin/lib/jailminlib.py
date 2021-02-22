# core modules
import os
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

def getVars(VarFile = None):
  # load default vars
  DefaultVars = util.readYamlFile(TemplatePath + '/jails/default/vars.yaml')

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
    for key in VarDict['props'].keys():
      template['props'][key] = VarDict['props'][key]

  # support command-line jail naming
  if 'JailName' in opts:
    template['name'] = opts['JailName']

  # post-merge var processing
  # iterate config selectively: light pass through tasks
  DefaultVars = {
    'JAILROOT': '/zroot/iocage/jails/{}/root/'.format(template['name']),
    'TEMPLATEROOT': '{}/templates/{}/'.format(TemplatePath, opts['TemplateName'])
  }

  if 'tasks' in template:
    for task in template['tasks']:
      for key in task.keys():
        if (type(task[key]) is str):
          for VarName in re.findall('\$\$[A-Za-z]+\$\$', task[key]):
            task[key] = task[key].replace(VarName, DefaultVars[VarName[2:-2]])

  # light template validation
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
