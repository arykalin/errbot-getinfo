import re
import logging
import string
from datetime import datetime
from tools import exec_remote
from tools import exec_remote_karaf
from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd, webhook

from config import KARAF_LIST
from config import PORTAL_LIST
from config import OPENAM_LIST

host_inventory = {}


class ExecMsgParams(object):
    def __init__(self, host_list, commands, match, host_type='default'):
        self.log = logging.getLogger("errbot.plugins.%s" % self.__class__.__name__)
        self.match = match
        self.host_list = sorted(host_list)
        self.commands = commands
        self.host_type = host_type
    def exec(self):
        msg_dict = {}
        msg_dict.clear()
        # host_inventory = {'hostname': 'None'}
        host_frm_msg = re.match("(.*)(\s+on\s+)(.*)", self.match.group(4))
        if host_frm_msg:
            host_frm_msg = host_frm_msg.group(3)
            self.log.debug("pattern match working with {}".format(host_frm_msg))
            for idx, h in enumerate(self.host_list):
                if host_frm_msg in h:
                    self.log.debug("{} match {} in {} updating dict {} to {}".format(host_frm_msg, self.host_list[idx], self.host_list,
                                                                                     host_inventory, h))
                    host_inventory['hostname'] = self.host_list[idx]
                    self.log.debug("hostname in dict {} is {}".format(host_inventory, host_inventory['hostname']))
                else:
                    self.log.debug("host {} not found in {}".format(host_frm_msg,self.host_list))
            host = host_inventory['hostname']
            if host == 'None':
                msg_dict[host] = "host {} not found in hosts list {}".format(host_frm_msg, self.host_list)
            else:
                if self.host_type == 'karaf':
                    m = exec_remote_karaf(host, self.commands)
                else:
                    m = exec_remote(host, self.commands)
                msg_dict[host] = m.exec()
        else:
            for host in self.host_list:
                self.log.debug('host is {}, going default, checking database used on {} :'.format(host_frm_msg,host))
                if self.host_type == 'karaf':
                    m = exec_remote_karaf(host, self.commands)
                else:
                    m = exec_remote(host, self.commands)
                msg_dict[host] = m.exec()
        return msg_dict

class GetInfo(BotPlugin):
    """Get info about environement"""
    @botcmd
    @arg_botcmd('host', type=str)
    # @re_botcmd(pattern=r"^show(.*)portal(.*)(version|vers)(.*)$")
    def getinfo_portal_versions(self, msg, host=None):
        """Get info about portal version"""
        commands = ["sudo cat /home/tomcat/portal/webapps/portal/WEB-INF/release.properties|sed 's/.*=//'"]
        m = exec_remote(host,commands).exec()
        yield('Portal on {} have version {}'.format(host, m))

    @botcmd
    @arg_botcmd('host', type=str)
    # @re_botcmd(pattern=r"^show(.*)portal(.*)(database|db)(.*)$", flags=re.IGNORECASE)
    def getinfo_portal_databases(self, msg, host=None):
        """Get info about portal database"""
        commands = ["sudo grep ^jdbc.mmdb.url /home/tomcat/portal/webapps/portal/WEB-INF/env.properties|sed 's#.*=.*jdbc:postgresql://##'"]
        m = exec_remote(host,commands).exec()
        yield('Portal on {} use database {}'.format(host, m))

    @botcmd
    @arg_botcmd('host', type=str)
    # @re_botcmd(pattern=r"^show(.*)openam(.*)(version|vers)(.*)$", flags=re.IGNORECASE)
    def getinfo_openam_versions(self, msg, host=None):
        """Get info about openam version"""
        commands = ["sudo grep  urlArgs.*v ""/home/openam/forgerock/openam-tomcat/webapps/openam/XUI/index.html |sed -e 's/.*=//' -e 's/\".*//'"]
        m = exec_remote(host,commands).exec()
        yield('OpenAM on {} have version {}'.format(host, m))

    @botcmd
    @arg_botcmd('host', type=str)
    #@re_botcmd(pattern=r"^show(.*)openam(.*)(database|db)(.*)$", flags=re.IGNORECASE)
    def getinfo_openam_databases(self, msg, host=None):
        """Get info about openam database"""
        commands = ["sudo grep jdbc:postgresql /home/openam/forgerock/openam-tomcat/conf/context.xml|tail -n 1|sed 's#.*postgresql://##'"]
        m = exec_remote(host,commands).exec()
        yield ('OpenAM on {} use database {}'.format(host, m))

    @botcmd
    @arg_botcmd('host', type=str)
    @arg_botcmd('--property', dest='property', type=str, default='com.qts.ump.dao.db.name')
    # @re_botcmd(pattern=r"^show(.*)karaf(.*)(database|db)(.*)$", flags=re.IGNORECASE)
    def getinfo_karaf_property(self, msg, host=None, property=None):
        """Get info about karaf property"""
        commands = ["config:list|grep {}".format(property)]
        m = exec_remote_karaf(host, commands).exec()
        yield('Karaf properties on {}:'.format(host))
        yield(m)
    @botcmd
    @arg_botcmd('host', type=str)
    def getinfo_karaf_features(self, mess, host=None):
        """Get info about karaf features versions"""
        commands = ["feature:info draas-proxy |head -n 1",
                    "feature:info carpathia-sync-service |head -n 1",
                    "feature:info ump-commons-feature |head -n 1",
                    "feature:info ump-roster-feature |head -n 1",]
        m = exec_remote_karaf(host, commands).exec()
        yield('Karaf on {} have features:'.format(host))
        m = str(m).split(',')
        for f in m:
            yield(f)

    @botcmd
    @arg_botcmd('host', type=str)
    @arg_botcmd('--service', dest='service', type=str)
    @arg_botcmd('--command', dest='command', type=str, default="restart")
    def getinfo_service_mngmt(self, mess, host=None, service=None, command=None):
        """Manage services"""
        commands = ['sudo systemctl {} {}'.format(command,service), 'sudo journalctl -n 6 -o cat|tail|head -n 4']
        yield("Running {} on {}".format(commands,host))
        m = exec_remote(host, commands).exec()
        m = str(m).split(',')
        for f in m:
            yield(f)

