#!/usr/bin/env python3.8
# coding=utf-8

from jinja2 import Template, Environment, FileSystemLoader
import json, yaml, os, time
import requests
import subprocess
from subprocess import Popen, PIPE
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROMETHEUS = 'https://prometheus.XXXX.ru'

def Prometheus(METRIC):
    QUEUE=[]
    response =requests.get(PROMETHEUS + '/api/v1/query', params={'query': METRIC })
    results = response.json()['data']['result']

    for result in results:
        p=result['metric']['queue']
        QUEUE.append

def Gitlab():
    print('вызов функции gitlab')

functions = {'prometheus':Prometheus, 'gitlab':Gitlab}

FILES='dashboard_test.jsonnet'
AUTH_TOKEN='eyJrIjoicFk1MXZGMXJQVTN2NlY1UjlmRzU5VllIcXZaeGVRbHEiLCJuIjoiZ3JhZm9ubmV0IiwiaWQiOjF9'
URL='https://grafana.usvc.XXX.ru/api/dashboards/db'


config_path = os.getenv("CONFIG_PATH") or "config.yaml"
with open(config_path, 'r') as f:
  CFG_JSON = yaml.load(f, Loader=yaml.SafeLoader)

D=CFG_JSON['dashboard']
L=D[0]

env = Environment(loader=FileSystemLoader('templates'))
templDasboard=env.get_template('dashboard.j2')
grafonnetfile = (templDasboard.render(L))


grafonnetfile=grafonnetfile.replace("True", "true")

f=open(FILES, 'w')
f.write(grafonnetfile)
f.close()

####
#templPannel=env.get_template('q_pannel.j2')

f=open(FILES, 'a')

for pannel in L['pannels']:

    TMPL=(pannel['template']+'.j2')
    templPannel=env.get_template(TMPL)

    if pannel['type'] == "static":

        if 'target' in pannel:
            TARGET=pannel['target']
            pannel.update(TARGET)
            
            if 'alert' in TARGET:
                ALERT=TARGET['alert']
                pannel.update(ALERT)

        pannels=(templPannel.render(pannel))
        pannels= pannels.replace("True", "true")
        f.write(pannels)

   elif pannel['type'] == "dinamic":
        dddd=pannel['gridPos']
        #print(dddd)
        coordinates=json.loads(dddd)
        print(coordinates)
        print(type(coordinates))
        W=coordinates['w']
        H=coordinates['h']
        X=coordinates['x']
        Y=coordinates['y']
        YY=Y
        XX=X
        #GRIDPOS={ }
        MODULE=pannel['module']['fun']
        METRIC=pannel['module']['metric']
        print(MODULE)
        print(METRIC)
        lst=functions[MODULE](METRIC)
        print(lst)
        #print('')
        for ITEM in lst:
            TITLE={'title':ITEM}
            GRIDPOS=f'{{h: {H}, w: {W}, x: {XX}, y: {YY}}}'
            XX=XX+W
            if XX >= 24:
                XX=0
                YY=YY+H
            GP={'gridPos': GRIDPOS}
            #print(GP)
            pannel.update(TITLE)
            pannel.update(GP)
            #print(pannel)
            print('')

            TARGET=pannel['target']
            pannel.update(TARGET)

            pannels=(templPannel.render(pannel))
            pannels= pannels.replace("True", "true")
            pannels= pannels.replace("$lebel", ITEM)
            f.write(pannels)

    else:
         print('unknown type')
f.close()

CMD = f'jsonnet {FILES}'
STDOUT = Popen(CMD, shell=True, stdout=PIPE).stdout
OUT = STDOUT.read()
JSON_CODE=json.loads(OUT)

FOLDERUID=L['folderID']
#PAYLOAD={"dashboard": JSON_CODE, "folderUid": FOLDERUID, "overwrite": True}
PAYLOAD={"dashboard": JSON_CODE, "folderId": FOLDERUID, "overwrite": True}

HEADERS={'Authorization': 'Bearer ' + AUTH_TOKEN}
RESPONCE = requests.post(url=URL, json=PAYLOAD, headers=HEADERS, verify=False, timeout=20 )
STATUS_CODE=RESPONCE.status_code
print('status_code:',STATUS_CODE)
