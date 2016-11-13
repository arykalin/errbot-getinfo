import re
import json
import string
from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd, webhook
from tools import look_for_host_in_host_list

from config import KARAF_LIST
from config import PORTAL_LIST
from config import OPENAM_LIST

class MessageParser(BotPlugin):
    @re_botcmd(pattern=r"(.*)(damn|fuck|stupid)(.*)$", flags=re.IGNORECASE,matchall=True)
    def be_nice(self, msg, match):
        yield "Could you be more nice (((?"

    @re_botcmd(pattern=r"(.*)(please)(.*)$", flags=re.IGNORECASE,matchall=True)
    def gracefull(self, msg, match):
        yield "Sure)"

#To avoid unnecessary match check regex for command and keyword
#TODO: Generare regex from msg_propeties dict -
#TODO: r = re.compile(r'\b(?:%s)\b' % '|'.join(msg_properties['keywords']))
#TODO: if re.match(r, 'logs'):print('match')
    @re_botcmd(pattern=r"(.*)(show|start|stop|restart)(.*)$", flags=re.IGNORECASE)
    @re_botcmd(pattern=r"(.*)(log|logs|db|database|features|ftrs|version|error|exception|portal|openam|karaf|ump)("
                       r".*)$",
               flags=re.IGNORECASE)
    def parse_msg(self, msg, match):
        msg_properties = {
            'commmand': ['show', 'start', 'stop','restart'],
            'service': ['portal','openam','karaf','ump'],
            'keywords': ['log','logs','db','database','features','ftrs','version','error','exception'],
            'host_groups': PORTAL_LIST+KARAF_LIST+OPENAM_LIST,
            'emotions': ['could','please','fuck','damn']
        }
        self.log.debug("Starting parse message {}".format(msg))
        m = str(msg)
        m = m.replace(',', '').replace('?', '')
        m = re.split(' ',m)
        self.log.debug("Removing commas from message {}".format(m))
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
                break
        #TODO: make keywords a list
        #'keyword':[]
        # host_inventory['keyword'].append(i)
        #check and split:
        #i = 'keyword'
        #if i in msg_properties['a']:m=msg_properties['keywords'][msg_properties['keywords'].index(i)]
        for h in m:
            host = look_for_host_in_host_list(h, msg_properties.get('host_groups')).search()
            if host is not None:
                host_inventory['hostname'] = host
                break
            self.log.debug('host inventory in parser {}'.format(host_inventory['hostname']))
        #TODO: make possible to use several host using a list

        for i in m:
            if i in msg_properties['emotions']:
                host_inventory['emotion'] = i

        self.log.debug('Host inventory is: {}'.format(host_inventory))
        #TODO: rewrite statements to compounds https://docs.python.org/3/reference/compound_stmts.html

        if host_inventory['service'] == 'karaf':
            if re.match("^features$|^ftrs$", host_inventory['keyword']) is not None:
                if host_inventory['hostname'] in KARAF_LIST:
                    self.log.debug('Trying to run karaf features from getinfo')
                    args = host_inventory['hostname']
                    yield from self.get_plugin('GetInfo').getinfo_karaf_features(msg, args)
                elif host_inventory['hostname'] == None:
                    for h in sorted(KARAF_LIST):
                        args = h
                        yield from self.get_plugin('GetInfo').getinfo_karaf_features(msg, args)
            if re.match("^db$|^databases$", host_inventory['keyword']) is not None:
                if host_inventory['hostname'] in KARAF_LIST:
                    self.log.debug('Trying to run karaf prperties from getinfo')
                    args = host_inventory['hostname']+' '+'--property com.qts.ump.dao.db.name'
                    yield from self.get_plugin('GetInfo').getinfo_karaf_property(msg, args)
                elif host_inventory['hostname'] == None:
                    for h in sorted(KARAF_LIST):
                        args = h
                        yield from self.get_plugin('GetInfo').getinfo_karaf_property(msg, args)

        if re.match("^start$|^stop$|^restart$", host_inventory['command']) is not None \
                and host_inventory['service'] is not None and host_inventory['hostname'] is not None:
            args = host_inventory['hostname']+' '+'--command '+host_inventory['command']+' '+'--service '+host_inventory['service']
            self.log.debug("Paasing arguemnts to getinfo_service_mngmt: {}".format(args))
            yield from self.get_plugin('GetInfo').getinfo_service_mngmt(msg, args)

        if host_inventory['command'] == 'show' and re.match("^log$|^logs$", host_inventory['keyword']):
            args = host_inventory['hostname']