import re
import json
import string
from datetime import datetime
from elasticsearch import Elasticsearch

from config import KARAF_LIST
from config import PORTAL_LIST
from config import OPENAM_LIST

class search(object):
    def __init__(self,msg):
        self.msg = msg
    def exec(self):
        es = Elasticsearch(['http://dev-test-elk.carpathia.com:9200'])
        our_q = {"from":0,"size":1,"query":{"bool":{"should":[{"match":{"host":host_dict['host']}},{"match":{' \
                '"source":"*catalina.out"}},{"match":{"message":"ERROR*"}}]}}}
        res = es.search(index="logstash-*",body=our_q)
        print("Got %d Hits:" % res['hits']['total'])
        for hit in res['hits']['hits']:
            print("%(@timestamp)s %(host)s: %(message)s" % hit["_source"])

msg_properties = {
    'commmand': ['show', 'start', 'stop','restart'],
    'service': ['portal','openam','karaf'],
    'keywords': ['log','logs','db','database','features','version','error','exception'],
    'host_groups': PORTAL_LIST+KARAF_LIST+OPENAM_LIST,
    'emotions': ['could','please','fuck','damn']
}
msg = 'could you show me portal on app01, please?'
print(msg)
exclude = set(string.punctuation)
msg = ''.join(ch for ch in msg if ch not in exclude)
m = re.split(' ',msg)
# print(m)
host_dict = {
    'host':'none',
    'service':'none',
    'keyword':'none',
    'command':'none',
    'emotion':'none'
}
for i in m:
    if i in msg_properties['commmand']:
        # print(i)
        host_dict['command'] = i
for i in m:
    if i in msg_properties['service']:
        # print(i)
        host_dict['service'] = i
for i in m:
    if i in msg_properties['keywords']:
        # print(i)
        host_dict['keyword'] = i
for i in m:
    hosts = msg_properties.get('host_groups')
    for idx, h in enumerate(hosts):
        if i in h:
            # print(hosts[idx])
            host_dict['host'] = hosts[idx]
            break
for i in m:
    if i in msg_properties['emotions']:
        # print(i)
        host_dict['emotion'] = i
print(msg)
print(host_dict)
if host_dict['keyword'] == 'error':
    search.exec(msg)



