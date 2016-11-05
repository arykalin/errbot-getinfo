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

    @re_botcmd(pattern=r"(.*)(show|start|stop|restart)(.*)$", flags=re.IGNORECASE)
    def parse_msg(self, msg, match):
        msg_properties = {
            'commmand': ['show', 'start', 'stop','restart'],
            'service': ['portal','openam','karaf'],
            'keywords': ['log','logs','db','database','features','version','error','exception'],
            'host_groups': PORTAL_LIST+KARAF_LIST+OPENAM_LIST,
            'emotions': ['could','please','fuck','damn']
        }
        self.log.debug(msg)
        m = str(msg)
        # m = m.replace(',', '').replace('?', '')
        exclude = set(string.punctuation)
        m = ''.join(ch for ch in m if ch not in exclude)
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
        if host_inventory['keyword'] == 'error' and host_inventory['hostname'] in PORTAL_LIST:
            host = host_inventory['hostname']
            self.log.debug('Executing search on host'.format(host))
            # s = search(host)
            # s.exec()
            yield 'Executing search on host'.format(host)
        if re.match(r"(version|vers)", host_inventory['keyword']):
            msg_dict = {}
            msg_dict.clear()
            commands = ["sudo cat /home/tomcat/portal/webapps/portal/WEB-INF/release.properties|sed 's/.*=//'"]
            host = host_inventory['hostname']
            if host in PORTAL_LIST:
                m = (self.get_plugin('GetInfo')(host, commands))
                reply = m.exec()
                yield('NEW Portal on {} have version {}'.format(host, reply))
            elif host == None:
                for host in PORTAL_LIST:
                    m = (self.get_plugin('GetInfo')(host, commands))
                    reply = m.exec()
                    yield('NEW Portal on {} have version {}'.format(host, reply))
            else:
                yield ('Sorry, I can not show portla version on {}'.format(host))
