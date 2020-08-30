# core modules
import os
import yaml
import sys
import json
import copy
# custom modules
import lib.util as util

AppBasePath = os.path.dirname(os.path.abspath(os.path.dirname(__file__) + '..'))
JailName = None
JailTemplate = None
JailHostTemplate = None
JailVarsHost = None
JailVars = None
YAMLKEY_PKG = 'pkg'
YAMLKEY_SERVICE = 'service'
YAMLKEY_CLI = 'cli'
YAMLKEY_IOCAGE = 'iocage'
YAMLKEY_JAILNAME = 'jailname'
YAMLKEY_VAR = 'var'
YAMLKEY_JAIL = 'jail'

def parseOptions():
    global JailName, JailTemplate, JailHostTemplate, JailVarsHost
    args = sys.argv.copy()
    args.pop(0)

    while len(args) > 0:
        cell = args.pop(0)
        if cell == '-t':
            JailTemplate = args.pop(0)
            continue
        if cell == '-h':
            JailHostTemplate = args.pop(0)
            continue
        if cell == '-v':
            JailVarsHost = args.pop(0)
            continue
        if (JailName == None):
            JailName = cell
            continue
        else:
            print ('ERROR: Unexpected param ' + cell)
            sys.exit(2)

def validateCliArguments():
    isSuccess = True
    while True:
        if (len(sys.argv) == 1):
            print('ERROR: Missing argument(s)')
            isSuccess = False
            break
        if JailName == None and JailHostTemplate == None:
            print('ERROR: Missing jail name')
            isSuccess = False
            break
        break

    if isSuccess == False:
        print('Usage: createjail jail_name [template]')
        sys.exit(1)

def readYamlFile(fname, vars={}):
    InFile = open(fname,'r')
    RawData = InFile.read()
    InFile.close()

    if YAMLKEY_VAR in vars:
        for key in vars[YAMLKEY_VAR]:
            RawData = RawData.replace('{{' + key + '}}', vars[YAMLKEY_VAR][key])
        print (RawData)
    doc = yaml.load(RawData, Loader=yaml.FullLoader)
    return doc

def getYamlInPath(TargetPath, BeginsWith):
    global JailVars
    ret = []
    for DirItem in os.listdir(TargetPath):
        ItemFullPath = TargetPath + '/' + DirItem
        if (DirItem.startswith(BeginsWith)
            and DirItem.endswith('.yaml') 
            and os.path.isfile(ItemFullPath)):
            ret.append(readYamlFile(TargetPath + '/' + DirItem, JailVars))

    return ret

def mergeJailTemplate(ThisJailTemplate, MasterDoc):
    global JailName
    for MergeDoc in getYamlInPath(AppBasePath + '/jails/' + ThisJailTemplate, 'createjail'):
        # merge dependent jails first
        if YAMLKEY_JAIL in MergeDoc:
            for DependentJail in MergeDoc[YAMLKEY_JAIL]:
                print ('Parsing jail template {}...'.format(DependentJail))
                mergeJailTemplate(DependentJail, MasterDoc)

        # print ('TemplateFile: ' + TemplateFile)
        for key in [YAMLKEY_PKG, YAMLKEY_SERVICE, YAMLKEY_CLI]:
            if key in MergeDoc:
                for item in MergeDoc[key]:
                    MasterDoc[key].append(item)

        if YAMLKEY_JAILNAME in MergeDoc:
            JailName = MergeDoc[YAMLKEY_JAILNAME]


def loadTemplate():
    global JailVars

    # load host variables
    JailVars = {}
    if JailVarsHost != None:
        readYamlFile('{}/hosts/{}/createjail-vars.yaml'.format(AppBasePath, JailVarsHost))
    print (JailVars)

    # load default/ base config
    doc = readYamlFile(AppBasePath + '/conf/createjail-default.yaml', JailVars)

    # load jail template if defined
    if JailTemplate != None:
        # this is resursive
        mergeJailTemplate(JailTemplate, doc)

    # load host template if defined
    # if JailVarsHost != None:
    #     MergeDoc = readYamlFile('{}/hosts/{}/createjail-vars.yaml'.format(AppBasePath, JailVarsHost))
    #     print (MergeDoc)
    #     for key in [YAMLKEY_PKG, YAMLKEY_SERVICE, YAMLKEY_CLI]:
    #         if key in MergeDoc:
    #             for item in MergeDoc[key]:
    #                 doc[key].append(item)

    #     if YAMLKEY_IOCAGE in MergeDoc:
    #         for key in MergeDoc[YAMLKEY_IOCAGE]:
    #             doc[YAMLKEY_IOCAGE][key] = MergeDoc[YAMLKEY_IOCAGE][key]


    print ('Jail name: {}'.format(JailName))
    print ('Jail template: {}'.format(JailTemplate))
    return doc

def execTemplate(doc):
    try:
        # core iocage commands
        cmd = 'sudo iocage create -r {} -n {}'.format(doc['iocage']['release'], JailName)
        print ('Mock exec: {}'.format(cmd))
        print ('Exit code: {}'.format(str(util.execNWait(cmd))))
        for key in doc['iocage'].keys():
            # blacklist keys from being applied to jail config
            if key in ['release', 'whatev']:
                continue

            # apply key to jail config
            value = doc['iocage'][key]
            if isinstance(value, bool):
                value = 1 if value == True else 0
            cmd = 'sudo iocage set {}={} {}'.format(key, value, JailName)
            print ('Mock exec: {}'.format(cmd))
            util.execNWait(cmd, isTest4Shell=False)

        # start jail (required to exec)
        cmd = 'sudo iocage start {}'.format(JailName)
        util.execNWait(cmd)
        print ('Mock exec: {}'.format(cmd))
    except Exception as err:
        print (err.args[0])
        return False


    # install packages
    for PkgName in doc['pkg']:
        cmd = 'sudo iocage exec {} pkg install -y {}'.format(JailName, PkgName)
        print ('Mock exec: {}'.format(cmd))
        util.execNWait(cmd)

    # start simple services
    for daemon in doc['service']:
        cmd = 'sudo iocage exec {} sysrc {}_enable=YES'.format(JailName, daemon)
        print ('Mock exec: {}'.format(cmd))
        util.execNWait(cmd)

        cmd = 'sudo iocage exec {} service {} start'.format(JailName, daemon)
        print ('Mock exec: {}'.format(cmd))
        util.execNWait(cmd)


    # create user account
    cmd = 'echo {} | pw useradd {} -h 0 -m -s {}'.format(doc['user']['pwd'], doc['user']['id'], doc['user']['shell'])
    print ('Create user: {}'.format(doc['user']['id']))
    util.execNWait('sudo iocage exec {} "{}"'.format(JailName, cmd))

    # exec raw cli
    for cmd in doc['cli']:
        if cmd.find('|') > -1 or cmd.find('>') > -1:
            cmd = '"' + cmd + '"'

        cmd = 'sudo iocage exec {} -- {}'.format(JailName, cmd)
        print ('Mock exec: {}'.format(cmd))
        util.execNWait(cmd)



def validatePython():
    if sys.version_info[0] < 3 or sys.version_info[1] < 7:
        raise Exception('Requires Python 3.7 and above')

def isNestedKeyExist(obj, NestedKey):
    _key = NestedKey.pop(0)
    if _key in obj:
        return isNestedKeyExist(obj[_key], NestedKey) if NestedKey else True
    else:
        return False 

def validateTemplate(doc):
    checks = {
        'ReleaseKey': ['iocage', 'release'],
        # 'SureFail': ['user', 'nokey'],
        'UserIdKey': ['user', 'id']
    }
    for key in checks.keys():
        if isNestedKeyExist(doc, copy.deepcopy(checks[key])) == False:
            raise Exception('Invalid template: missing key {}'.format(' -> '.join(checks[key])))

validatePython()
parseOptions()
doc = loadTemplate()
validateTemplate(doc)
validateCliArguments()
print (json.dumps(doc, indent=4, sort_keys=True))
execTemplate(doc)

# print ('Exit code: {}'.format(str(util.execNWait('sudo iocage destroy -f {}'.format(JailName)))))




