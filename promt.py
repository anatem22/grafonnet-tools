import datetime
import time
import requests

PROMETHEUS = 'https://prometheus.tusvc.bcs.ru'


response =requests.get(PROMETHEUS + '/api/v1/query', params={'query': 'avg(rabbitmq_queue_messages{queue=~"to.ef.*"}) by (queue)'})
results = response.json()['data']['result']

for result in results:
#    p=(result['metric'])
#    pr=p['queue']
#    print(pr)
    print(result['metric']['queue'])

QUEUE=[]

for result in results:
    p=result['metric']['queue']
    QUEUE.append(p)
print(QUEUE)
