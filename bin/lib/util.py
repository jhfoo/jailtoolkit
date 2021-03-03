# core modules
import re
import subprocess
import json
# public modules
import requests
import yaml

def getFromGit(AppConfig, fname):
  """Confirm code block necessary to GET raw GitHub private repo"""
  # print (json.dumps(AppConfig, indent=2))
  headers = {
    'Authorization': 'token {}'.format(AppConfig['github']['token']),
    'Accept': 'application/vnd.github.v3.raw'
  }
  url = 'https://raw.githubusercontent.com/{}/{}{}'.format(AppConfig['github']['RepoUrl'], AppConfig['github']['RepoBranch'], fname)
  res = requests.get(url, headers=headers)
  if res.status_code == 200:
    return res.text
  else:
    raise Exception('Unable to retrieve: {}'.format(url))

def execNWaitShell(cmd):
  """Executes command in shell and waits for completion"""
  child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out = child.communicate()[0].decode('utf-8').strip()
  print (out)
  return child.poll()

def execNWait(cmd, isTest4Shell=True, isContinueOnError=False, isPrintRealtime=True, isForceShellExec=False):
  """Executes command and waits for completion"""
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
        print (err)
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
        response += line
        if isPrintRealtime:
          print (line)

  except subprocess.TimeoutExpired as err:
    print ('*** Terminating process')
    child.kill()
    out, err = child.communicate()
    print (out.decode('utf-8'))
    print (err.decode('utf-8'))

def parseYaml(TextString, TemplateVars=None):
  """Apply variables and parse string as yaml"""

  if TemplateVars is not None:
    print ('Substituting {} variables...'.format(len(TemplateVars.keys())))
    for key in TemplateVars.keys():
      TextString = TextString.replace('{{' + key + '}}', str(TemplateVars[key]))

  # replace unmapped {{varname}} into $$varname$$
  for key in re.findall('{{[A-Za-z]+}}', TextString):
    VarName = key[2:-2]
    TextString = TextString.replace(key, '$${}$$'.format(VarName))
  doc = yaml.load(TextString, Loader=yaml.FullLoader)
  return doc

def readTextFile(fname):
  """Reads text file into str object and returns"""
  InFile = open(fname,'r')
  TextString = InFile.read()
  InFile.close()

  return TextString

# Loads yaml file, applies variables, returns Dictionary obj
def readYamlFile(fname, TemplateVars=None):
  """Parse YAML file into Dictionary"""
  RawData = readTextFile(fname)
  return parseYaml(RawData, TemplateVars)
