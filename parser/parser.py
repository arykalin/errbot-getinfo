import re
import json
import string
from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd, webhook

from config import KARAF_LIST
from config import PORTAL_LIST
from config import OPENAM_LIST

class MessageParser(BotPlugin):
    @re_botcmd(pattern=r"(.*)(damn|fuck|stupid)(.*)$", flags=re.IGNORECASE,matchall=True)
    def be_nice(self, msg, match):
        yield "Could you be more nice (((?"

    @re_botcmd(pattern=r"(.*)(please)(.*)$", flags=re.IGNORECASE,matchall=True)
    def gracefull(self, msg, match):
        yield "It nice to hear"

#To avoid unnecessary match check regex for command and keyword
    @re_botcmd(pattern=r"(.*)(show|start|stop|restart)(.*)$", flags=re.IGNORECASE)
    @re_botcmd(pattern=r"(.*)(log|logs|db|database|features|ftrs|version|error|exception)(.*)$",
               flags=re.IGNORECASE)
    def parse_msg(self, msg, match):
        msg_properties = {
            'commmand': ['show', 'start', 'stop','restart'],
            'service': ['portal','openam','karaf'],
            'keywords': ['log','logs','db','database','features','ftrs','version','error','exception'],
            'host_groups': PORTAL_LIST+KARAF_LIST+OPENAM_LIST,
            'emotions': ['could','please','fuck','damn']
        }
        self.log.debug(msg)
        m = str(msg)
        m = m.replace(',', '').replace('?', '')
        # exclude = set(string.punctuation)
        # m = ''.join(ch for ch in m if ch not in exclude)
        m = re.split(' ',m)
        print(m)
        # self.log.debug(m)
        host_inventory = {
            'hostname':None,
            'service':None,
            'keyword':None,
            'command':None,
            'emotion':None
        }
        for i in m:
            if i in msg_properties['commmand']:
                host_inventory['command'] = i
        for i in m:
            if i in msg_properties['service']:
                host_inventory['service'] = i
        for i in m:
            if i in msg_properties['keywords']:
                host_inventory['keyword'] = i
        for i in m:
            hosts = msg_properties.get('host_groups')
            for idx, h in enumerate(hosts):
                if i in h:
                    host_inventory['hostname'] = hosts[idx]
                    break
        for i in m:
            if i in msg_properties['emotions']:
                # self.log.debug(i)
                host_inventory['emotion'] = i
        print(m)
        print('host inventory in parser {}'.format(host_inventory))

        if host_inventory['service'] == 'karaf' and (host_inventory['keyword'] == 'features'
                                        or host_inventory['keyword'] == 'ftrs'):
            if host_inventory['hostname'] in KARAF_LIST:
                print('Trying to run karaf features from getinfo')
                args = host_inventory['hostname']
                yield from self.get_plugin('GetInfo').getinfo_karaf_features(msg, args)
            elif host_inventory['hostname'] == None:
                for h in sorted(KARAF_LIST):
                    args = h
                    yield from self.get_plugin('GetInfo').getinfo_karaf_features(msg, args)