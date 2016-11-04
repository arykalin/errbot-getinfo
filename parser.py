import re
import json
import string
from config import KARAF_LIST
from config import PORTAL_LIST
from config import OPENAM_LIST
#TODO:
#rewrite search algortim:
#split the wrods with whitespaces or commas
#search the keywords above dictionaty
#like:
#show me the latest portal exception on app02
#show - exec1
#logs - exec2
#portal - what logs
#latest
#on app02 - where
#from the command:
#show exception(latest) from catalina.out on app02

parse_msg = {
    'commmand': ['show', 'start', 'stop','restart'],
    'service': ['portal','openam','karaf'],
    'keywords': ['log','logs','db','database','features','version','error','exception'],
    'host_groups': PORTAL_LIST+KARAF_LIST+OPENAM_LIST,
    'emotions': ['could','please','fuck','damn']
}
msg = 'could you show me portal db on app01, please?'
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
    if i in parse_msg['commmand']:
        # print(i)
        host_dict['command'] = i
for i in m:
    if i in parse_msg['service']:
        # print(i)
        host_dict['service'] = i
for i in m:
    if i in parse_msg['keywords']:
        # print(i)
        host_dict['keyword'] = i
for i in m:
    hosts = parse_msg.get('host_groups')
    for idx, h in enumerate(hosts):
        if i in h:
            # print(hosts[idx])
            host_dict['host'] = hosts[idx]
            break
for i in m:
    if i in parse_msg['emotions']:
        # print(i)
        host_dict['emotion'] = i
print(msg)
print(host_dict)


