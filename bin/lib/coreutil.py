# This module cannot include public mods as it is loaded before any are installed
# core modules
import subprocess
import logging

def execNWaitShell(cmd):
  """Executes command in shell and waits for completion"""
  child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out = child.communicate()[0].decode('utf-8').strip()

  # log to file
  logger = logging.getLogger('default')
  logger.debug(out)

  return child.poll()

def execNWait(cmd, isTest4Shell=True, isContinueOnError=False, isPrintRealtime=True, isForceShellExec=False, DebugPath='./debug/'):
  """Executes command and waits for completion"""
  logger = logging.getLogger('default')
  logger.debug('CMD: {}'.format(cmd))

  if isTest4Shell:
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
        logger = logging.getLogger('default')
        logger.error(err)

        print ('ERROR: See exec.error.log for details')
      if line == '':
        # child has terminated: exit fn
        code = child.poll()
        if code is not None:
          if code > 0 and not isContinueOnError:
            raise Exception('FAILED (code {}): {}'.format(code, cmd))
          # print ('Exit code: {}'.format(str(code)))

          if isPrintRealtime:
            return code
          # else
          return {
            'output': response,
            'ExitCode': code
          }
      else:
        # log to file
        logger = logging.getLogger('default')
        logger.debug(line)

        response += line
        if isPrintRealtime:
          print (line)

  except subprocess.TimeoutExpired as err:
    print ('*** Terminating process')
    child.kill()
    out, err = child.communicate()
    logger = logging.getLogger('default')
    logger.debug(out.decode('utf-8'))
    logger.error(err.decode('utf-8'))

    print (out.decode('utf-8'))
    print (err.decode('utf-8'))