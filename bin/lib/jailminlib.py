# core modules
import os
import re
import json
# public modules
# custom modules
import lib.util as util

AppBasePath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

def getTemplates(isTemplate = True):
  """Convert template list as returned from iocage as dictionary"""
  templates = []
  # switch between templates and jails
  TempString = '-t' if isTemplate else ''
  ExecResult = util.execNWait('iocage list {}'.format(TempString), isPrintRealtime = False)
  if ExecResult['ExitCode'] == 0:
    lines = ExecResult['output'].split('\n')
    if len(lines) > 3:
      lines.pop(0)
      lines.pop(0)
      lines.pop(0)

    for line in lines:
      columns = line.split('|')
      if len(columns) == 7:
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
  """Return value in a type recognized by iocage"""
  if isinstance(value, bool):
    return 1 if value else 0
  # if (type(value) is str):
  return '"{}"'.format(value)

def getJailProps(JailName):
  """Get jail properties as returned by iocage"""
  RawJailProps = util.execNWait('iocage get all {}'.format(JailName), isPrintRealtime = False, isContinueOnError = True)
  if RawJailProps['ExitCode'] != 0:
    # jail does not exist
    return None

  props = {}
  for line in RawJailProps['output'].split('\n'):
    columns = line.split(':')
    if len(columns) > 1:
      props[columns[0]] = columns[1]
  return props

def smartGetFile(AppConfig, DynParam, PathFormat, LocalPrefix):
  """Either get file locally or from GitHub"""
  if DynParam.startswith('github'):
    FinalPath = PathFormat.format(DynParam[7:])
    print ('FinalPath: GITHUB {}'.format(FinalPath))
    return util.getFromGit(AppConfig, FinalPath)

  # else
  FinalPath = LocalPrefix + PathFormat.format(DynParam)
  print ('FinalPath: LOCAL {}'.format(FinalPath))
  return util.readTextFile(FinalPath)

def getVars(opts):
  """Merge default and user-defined variable files into a single dictionary"""
  # load default vars
  DefaultVars = {}
  if 'DefaultVars' not in opts['AppConfig']:
    # default handler when DefaultVars not specified
    DefaultVars = util.readYamlFile(opts['TemplatePath'] + '/jails/default/vars.yaml')
  else:
    DefaultVars = util.parseYaml(smartGetFile(opts['AppConfig'], opts['AppConfig']['DefaultVars'], '/jails/default/vars.yaml', opts['TemplatePath']))

  if 'VarFile' not in opts:
    return DefaultVars

  CustomVars = util.parseYaml(smartGetFile(opts['AppConfig'], opts['VarFile'], '/jails/{}/vars.yaml', opts['TemplatePath']))

  # custom vars override defaults
  CustomVarsKeys = CustomVars['vars'].keys()
  for key in DefaultVars['vars'].keys():
    if key not in CustomVarsKeys:
      CustomVars['vars'][key] = DefaultVars['vars'][key]

  print (json.dumps(CustomVars, indent=2))
  return CustomVars

def getMergedTemplate(opts):
  """Load jailmin template and apply variables"""
  VarDict = opts['vars']
  TemplateVars = VarDict['vars'] if ('vars' in VarDict.keys()) else {}
  TextFile = smartGetFile(opts['AppConfig'], opts['TemplateName'], '/templates/{}/template.yaml', opts['TemplatePath'])
  template = util.parseYaml(TextFile, TemplateVars)
  # template = util.readYamlFile(opts['TemplatePath'] + '/templates/' + opts['TemplateName'] + '/template.yaml', vars)
  if 'props' not in template:
    template['props'] = {}

  # support command-line jail naming
  if 'JailName' in opts:
    template['name'] = opts['JailName']
  if 'Ip4Addr' in opts:
    template['props']['ip4_addr'] = opts['Ip4Addr']

  # props in VarFile overrides template defaults
  if 'props' in VarDict.keys():
    for key in VarDict['props'].keys():
      template['props'][key] = VarDict['props'][key]

  # post-merge var processing
  # iterate config selectively: light pass through tasks
  DefaultVars = {
    'JAILROOT': '/zroot/iocage/jails/{}/root/'.format(template['name']),
    'TEMPLATEROOT': '{}/templates/{}/'.format(opts['TemplatePath'], opts['TemplateName']),
    'JAILNAME': template['name']
  }

  # update vars so nested templates can substitute early
  for key in DefaultVars:
    TemplateVars[key] = DefaultVars[key]

  if 'tasks' in template:
    for task in template['tasks']:
      for key in task:
        if type(task[key]) is str:
          for VarName in re.findall(r'$$[A-Za-z]+$$', task[key]):
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
  if (props is not None and props['state'] == 'up'):
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
  if isinstance(value, bool):
    return 1 if value else 0
  if isinstance(value, int):
    return str(value)
  if isinstance(value, str):
    return value

  # else: unexpected type
  raise Exception('Unhandled value type: {}'.format(type(value)))
