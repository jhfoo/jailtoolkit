import os
import yaml
import sys
import subprocess

AppBasePath = os.path.dirname(os.path.abspath(os.path.dirname(__file__) + '..'))
JailName = None
JailTemplate = None

def parseOptions():
    global JailName, JailTemplate
    args = sys.argv.copy()
    args.pop(0)

    while len(args) > 0:
        cell = args.pop(0)
        if (cell == '-t'):
            JailTemplate = args.pop(0)
        else:
            if (JailName == None):
                JailName = cell
            else:
                print ('ERROR: Unexpected param ' + cell)
                sys.exit(2)

def validateCliArguments():
    if (len(sys.argv) == 1):
        print('Usage: createjail jail_name [template]')
        sys.exit(1)

def loadTemplate():
    print ('Jail name: {}'.format(JailName))
    print ('Jail template: {}'.format(JailTemplate))
    InFile = open(AppBasePath + '/conf/createjail-default.yaml','r')
    return yaml.load(InFile.read(), Loader=yaml.FullLoader)

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

    # exec raw cli
    for cmd in doc['cli']:
        cmd = 'sudo iocage exec {} {}'.format(JailName, cmd)
        print ('Mock exec: {}'.format(cmd))
        print ('Exit code: {}'.format(str(execNWait(cmd))))

def execNWait(cmd):
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

validateCliArguments()
parseOptions()
doc = loadTemplate()
print (doc)
execTemplate(doc)

print ('Exit code: {}'.format(str(execNWait('sudo iocage destroy -f {}'.format(JailName)))))




