# core modules
import os
import sys
import json
import copy
import re
# 3P modules
# sys.path.append('/usr/local/lib/python3.7/site-packages/iocage_lib')
# import iocage
# custom modules
import lib.util as util

jails = [] 
actions = {
    'SetProperty': {
        'key': '',
    },
    'GetProperty': {
        'key': '',
    },
    'IsUpdate': False,
    'jails': []
}

def getProperty(args):
    global actions

    if len(args) == 0:
        print ('ERROR: Missing key=value param for getprop')
        sys.exit(2)

    # all good
    actions['GetProperty']['key'] = args.pop(0).strip()
    print ('key = {}'.format(actions['GetProperty']['key']))

def setProperty(args):
    global actions

    if len(args) == 0:
        print ('ERROR: Missing key=value param for setprop')
        sys.exit(2)

    KeyValue = args.pop(0)
    # check if format is key=value
    KeyValueSplit = KeyValue.split('=')
    if len(KeyValueSplit) < 2:
        print ('ERROR: Invalid key=value param format for setprop')
        sys.exit(2)

    # all good
    actions['SetProperty']['key'] = KeyValueSplit.pop(0).strip()
    actions['SetProperty']['value'] = '='.join(KeyValueSplit).strip()
    print ('key = {}'.format(actions['SetProperty']['key']))
    print ('value = {}'.format(actions['SetProperty']['value']))

def getJailNames():
    names = []
    for jail in jails:
        names.append(jail['name'])
    return names

def doTest(args):
    print ('Hi!')

def parseOptions():
    global actions
    args = sys.argv.copy()
    args.pop(0)

    while len(args) > 0:
        cell = args.pop(0)
        if cell == 'setprop':
            setProperty(args)
            continue
        if cell == 'getprop':
            getProperty(args)
            continue
        if cell == 'update':
            actions['IsUpdate'] = True
            continue
        if cell == 'test':
            doTest(args)
            continue
        else:
            # everything from here on must be jails
            args.append(cell)
            # actions['jails'].append(cell)
            while len(args) > 0:
                jail = args.pop(0)
                if jail == 'all':
                    actions['jails'] = getJailNames()
                    break
                else:
                    actions['jails'].append(jail)

    if len(actions['jails']) == 0:
        print ('ERROR: Missing jail list')
        sys.exit(2)

def getJails():
    output = util.execNWait('sudo iocage list', isPrintRealtime=False)
    lines = output['output'].splitlines()
    jails = []
    isHeader = True
    for line in output['output'].splitlines():
        fields = line.split('|')
        if len(fields) == 7:
            if isHeader:
                isHeader = False
            else:
                fields.pop(0)
                jails.append({
                    'jid': fields[0].strip(),
                    'name': fields[1].strip(),
                    'state': fields[2].strip(),
                    'release': fields[3].strip(),
                    'ip4': fields[4].strip()
                })

    return jails

def execActions():
    if actions['GetProperty']['key'] != '':
        for JailName in actions['jails']:
            cmd = 'sudo iocage get {} {}'.format(actions['GetProperty']['key'], JailName)
            resp = util.execNWait(cmd, isTest4Shell=False, isPrintRealtime=False)
            print ('{}: {}'.format(JailName, resp['output'].strip()))
    elif actions['SetProperty']['key'] != '':
        for JailName in actions['jails']:
            cmd = 'sudo iocage set {}={} {}'.format(actions['SetProperty']['key'], actions['SetProperty']['value'], JailName)
            print ('Mock exec: {}'.format(cmd))
            util.execNWait(cmd, isTest4Shell=False)
    elif actions['IsUpdate'] != '':
        for JailName in actions['jails']:
            cmd = 'sudo iocage update {}'.format(JailName)
            print ('Mock exec: {}'.format(cmd))
            
jails = getJails()
parseOptions()
execActions()
