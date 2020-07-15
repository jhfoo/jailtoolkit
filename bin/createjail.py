import os
import yaml
import sys
import subprocess

AppBasePath = os.path.dirname(os.path.abspath(os.path.dirname(__file__) + '..'))
JailName = None
JailTemplate = None
JailHostTemplate = None
YAMLKEY_PKG = 'pkg'
YAMLKEY_SERVICE = 'service'
YAMLKEY_CLI = 'cli'
YAMLKEY_IOCAGE = 'iocage'
YAMLKEY_JAILNAME = 'jailname'

def parseOptions():
    global JailName, JailTemplate, JailHostTemplate
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
            isSuccess = false
            break
        if JailName == None and JailHostTemplate == None:
            print('ERROR: Missing jail name')
            isSuccess = false
            break
        break

    if isSuccess == False:
        print('Usage: createjail jail_name [template]')
        sys.exit(1)

def readYamlFile(fname):
    InFile = open(fname,'r')
    doc = yaml.load(InFile.read(), Loader=yaml.FullLoader)
    InFile.close()
    return doc

def getYamlInPath(TargetPath):
    ret = []
    for DirItem in os.listdir(TargetPath):
        ItemFullPath = TargetPath + '/' + DirItem
        if (DirItem.startswith('createjail')
            and DirItem.endswith('.yaml') 
            and os.path.isfile(ItemFullPath)):
            ret.append(readYamlFile(TargetPath + '/' + DirItem))

    return ret

def loadTemplate():
    global JailName
    doc = readYamlFile(AppBasePath + '/conf/createjail-default.yaml')

    # load jail template if defined
    if JailTemplate != None:
        for MergeDoc in getYamlInPath(AppBasePath + '/jails/' + JailTemplate):
            # print ('TemplateFile: ' + TemplateFile)
            for key in [YAMLKEY_PKG, YAMLKEY_SERVICE, YAMLKEY_CLI]:
                if key in MergeDoc:
                    for item in MergeDoc[key]:
                        doc[key].append(item)

    # load host template if defined
    if JailHostTemplate != None:
        MergeDoc = readYamlFile('{}/hosts/{}/create-host.yaml'.format(AppBasePath, JailHostTemplate))
        print (MergeDoc)
        for key in [YAMLKEY_PKG, YAMLKEY_SERVICE, YAMLKEY_CLI]:
            if key in MergeDoc:
                for item in MergeDoc[key]:
                    doc[key].append(item)

        if YAMLKEY_IOCAGE in MergeDoc:
            for key in MergeDoc[YAMLKEY_IOCAGE]:
                doc[YAMLKEY_IOCAGE][key] = MergeDoc[YAMLKEY_IOCAGE][key]

        if YAMLKEY_JAILNAME in MergeDoc:
            JailName = MergeDoc[YAMLKEY_JAILNAME]

    print ('Jail name: {}'.format(JailName))
    print ('Jail template: {}'.format(JailTemplate))
    return doc

def execTemplate(doc):
    cmd = 'sudo iocage create -r {} -n {}'.format(doc['iocage']['release'], JailName)
    print ('Mock exec: {}'.format(cmd))
    print ('Exit code: {}'.format(str(execNWait(cmd))))
    for key in doc['iocage'].keys():
        if key not in ['release', 'whatev']:
            value = doc['iocage'][key]
            if isinstance(value, bool):
                value = 1 if value == True else 0
            cmd = 'sudo iocage set {}={} {}'.format(key, value, JailName)
            print ('Mock exec: {}'.format(key, value, JailName))
            print ('Exit code: {}'.format(str(execNWait(cmd))))

    # start jail (required to exec)
    cmd = 'sudo iocage start {}'.format(JailName)
    print ('Mock exec: {}'.format(cmd))
    print ('Exit code: {}'.format(str(execNWait(cmd))))

    # install packages
    for PkgName in doc['pkg']:
        cmd = 'sudo iocage exec {} pkg install -y {}'.format(JailName, PkgName)
        print ('Mock exec: {}'.format(cmd))
        print ('Exit code: {}'.format(str(execNWait(cmd))))

    # start simple services
    for daemon in doc['service']:
        cmd = 'sudo iocage exec {} sysrc {}_enable=YES'.format(JailName, daemon)
        print ('Mock exec: {}'.format(cmd))
        print ('Exit code: {}'.format(str(execNWait(cmd))))

        cmd = 'sudo iocage exec {} service {} start'.format(JailName, daemon)
        print ('Mock exec: {}'.format(cmd))
        print ('Exit code: {}'.format(str(execNWait(cmd))))


    # create user account
    cmd = 'echo {} | pw useradd {} -h 0 -m -s {}'.format(doc['user']['pwd'], doc['user']['id'], doc['user']['shell'])
    print ('Create user exit code: {}'.format(str(execNWait('sudo iocage exec {} "{}"'.format(JailName, cmd)))))

    # exec raw cli
    for cmd in doc['cli']:
        if cmd.find('|') > -1 or cmd.find('>') > -1:
            cmd = '"' + cmd + '"'

        cmd = 'sudo iocage exec {} -- {}'.format(JailName, cmd)
        print ('Mock exec: {}'.format(cmd))
        print ('Exit code: {}'.format(str(execNWait(cmd))))

def execNWaitShell(cmd):
    child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = child.communicate()[0].decode('utf-8').strip()
    print (out)
    return child.poll()

def execNWait(cmd):
    if cmd.find('|') > -1 or cmd.find('>') > -1:
        # exec in shell mode
        return execNWaitShell(cmd)

    # shell = false
    cmd = cmd.split()
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        while True:
            line = child.stdout.readline().decode('utf-8').strip()
            err = child.stderr.readline().decode('utf-8').strip()
            # always print error messages
            if err != '':
                print (err)
            if line == '':
                # child has terminated: exit fn
                code = child.poll()
                if code != None:
                    return code
            else:
                print (line)

    except subprocess.TimeoutExpired as err:
        print ('*** Terminating process')
        child.kill()
        out, err = child.communicate()
        print (out.decode('utf-8'))
        print (err.decode('utf-8'))

parseOptions()
validateCliArguments()
doc = loadTemplate()
print (doc)
# execTemplate(doc)

# print ('Exit code: {}'.format(str(execNWait('sudo iocage destroy -f {}'.format(JailName)))))




