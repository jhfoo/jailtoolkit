import subprocess

def execNWaitShell(cmd):
    child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = child.communicate()[0].decode('utf-8').strip()
    print (out)
    return child.poll()

def execNWait(cmd, isTest4Shell=True, isContinueOnError=False, isPrintRealtime=True, isForceShellExec=False):
    if isTest4Shell == True:
        if isForceShellExec or cmd.find('|') > -1 or cmd.find('>') > -1 or cmd.find('"') > -1:
            # exec in shell mode
            return execNWaitShell(cmd)

    # shell = false
    cmd = cmd.split()
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    response = ''
    try:
        while True:
            line = child.stdout.read().decode('utf-8')
            err = child.stderr.read().decode('utf-8')
            # always print error messages
            if err != '':
                print (err)
            if line == '':
                # child has terminated: exit fn
                code = child.poll()
                if code != None:
                    if code > 0 and isContinueOnError == False:
                        raise Exception('FAILED (code {}): {}'.format(code, cmd))
                    # print ('Exit code: {}'.format(str(code)))

                    if isPrintRealtime:
                        return code
                    else:
                        return {
                            'output': response,
                            'ExitCode': code
                        }
            else:
                response += line
                if isPrintRealtime:
                    print (line)
        
    except subprocess.TimeoutExpired as err:
        print ('*** Terminating process')
        child.kill()
        out, err = child.communicate()
        print (out.decode('utf-8'))
        print (err.decode('utf-8'))
