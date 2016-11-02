import paramiko
import re
import logging

from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd, webhook

from config import SSH_KEY
from config import SSH_USER
from config import KARAF_LIST
from config import PORTAL_LIST
from config import OPENAM_LIST

class exec_remote(object):
    def __init__(self, hostname, commands):
        self.hostname = hostname
        self.commands = commands
        self.log = logging.getLogger("errbot.plugins.%s" % self.__class__.__name__)

    def exec(self):
        k = paramiko.RSAKey.from_private_key_file(SSH_KEY)
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.log.debug("connecting")
        c.connect(self.hostname, username=SSH_USER, pkey=k)
        self.log.debug("Commands are {}".format(self.commands))
        l = []
        for command in self.commands:
            self.log.debug("Executing {}".format(command))
            stdin, stdout, stderr = c.exec_command(command, get_pty=True)
            for line in stdout:
                line = line.rstrip()
                l.append(line)

        c.close()

        #return ', '.join( repr(e).strip() for e in l)
        return ', '.join( repr(e) for e in l)


class exec_remote_karaf(exec_remote):
    def exec(self):
        user = 'karaf'
        password = 'karaf'
        port = 8101
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.log.debug("connecting")
        c.connect(self.hostname, username=user, password=password, port=port)
        self.log.debug("Commands are {}".format(self.commands))
        l = []
        ansi_escape = re.compile(r'\x1b[^m]*m')
        for command in self.commands:
            self.log.debug("Executing {}".format(command))
            stdin, stdout, stderr = c.exec_command(command, get_pty=True)
            for line in stdout:
                line = ansi_escape.sub('', line).rstrip()
                l.append(line)

        c.close()

        #return ', '.join( repr(e).strip() for e in l)
        return ', '.join( repr(e) for e in l)

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
        host_dict = {'hostname': 'None'}
        host_frm_msg = re.match("(.*)(\s+on\s+)(.*)", self.match.group(4))
        if host_frm_msg:
            host_frm_msg = host_frm_msg.group(3)
            self.log.debug("pattern match working with {}".format(host_frm_msg))
            for idx, h in enumerate(self.host_list):
                if host_frm_msg in h:
                    self.log.debug("{} match {} in {} updating dict {} to {}".format(host_frm_msg,self.host_list[idx],self.host_list,
                                                                      host_dict,h))
                    host_dict['hostname'] = self.host_list[idx]
                    self.log.debug("hostname in dict {} is {}".format(host_dict,host_dict['hostname']))
                else:
                    self.log.debug("host {} not found in {}".format(host_frm_msg,self.host_list))
            host = host_dict['hostname']
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

    @re_botcmd(pattern=r"^show(.*)portal(.*)(version|vers)(.*)$")
    def portal_versions(self, msg, match):
        """Get info about portal version"""
        host_list = PORTAL_LIST
        commands = ["sudo cat /home/tomcat/portal/webapps/portal/WEB-INF/release.properties|sed 's/.*=//'"]
        d = ExecMsgParams(host_list, commands, match).exec()
        for key, value in d.items():yield('Portal on {} have version {}'.format(key, value))

    @re_botcmd(pattern=r"^show(.*)portal(.*)(database|db)(.*)$", flags=re.IGNORECASE)
    def portal_databases(self, msg, match):
        """Get info about portal database"""
        host_list = PORTAL_LIST
        commands = ["sudo grep ^jdbc.mmdb.url /home/tomcat/portal/webapps/portal/WEB-INF/env.properties|sed 's#.*=.*jdbc:postgresql://##'"]
        d = ExecMsgParams(host_list, commands, match).exec()
        for key, value in d.items():yield('Portal on {} use database {}'.format(key, value))

    @re_botcmd(pattern=r"^show(.*)openam(.*)(version|vers)(.*)$", flags=re.IGNORECASE)
    def openam_versions(self, msg, match):
        """Get info about openam version"""
        host_list = OPENAM_LIST
        commands = ["sudo grep  urlArgs.*v ""/home/openam/forgerock/openam-tomcat/webapps/openam/XUI/index.html |sed -e 's/.*=//' -e 's/\".*//'"]
        d = ExecMsgParams(host_list, commands, match).exec()
        for key, value in d.items():yield('OpenAM on {} have version {}'.format(key, value))

    @re_botcmd(pattern=r"^show(.*)openam(.*)(database|db)(.*)$", flags=re.IGNORECASE)
    def openam_databases(self, msg, match):
        """Get info about openam database"""
        host_list = OPENAM_LIST
        commands = ["sudo grep jdbc:postgresql /home/openam/forgerock/openam-tomcat/conf/context.xml|tail -n 1|sed 's#.*postgresql://##'"]
        d = ExecMsgParams(host_list, commands, match).exec()
        for key, value in d.items():yield('OpenAM on {} use database {}'.format(key, value))

    @re_botcmd(pattern=r"^show(.*)karaf(.*)(database|db)(.*)$", flags=re.IGNORECASE)
    def karaf_database(self, msg, match):
        """Get info about karaf database"""
        host_list = KARAF_LIST
        commands = ["config:list|grep com.qts.ump.dao.db.name"]
        host_type = 'karaf'
        d = ExecMsgParams(host_list, commands, match, host_type).exec()
        for key, value in d.items():yield('UMP on {} use database {}'.format(key, value))

    @re_botcmd(pattern=r"^(stop|start|restart)(.*)(openam|portal|ump)(.*)$", flags=re.IGNORECASE)
    def service_restart(self, msg, match):
        """Get info about karaf database"""
        host_list = set().union(PORTAL_LIST, KARAF_LIST, OPENAM_LIST)
        commands = []
        e = match.group(1)
        s = match.group(3)
        cmd = 'sudo systemctl {} {}'.format(e,s)
        commands.append(cmd)
        # host_frm_msg = re.match("(.*)(\s+on\s+)(.*)", match.group(4))
        # print('will run {} on {}'.format(commands, host_frm_msg))
        print(match.group(4))
        if "on" in match.group(4):
           d = ExecMsgParams(host_list, commands, match).exec()
           for key, value in d.items():yield('Executed {} on {} with result {}'.format(commands, key, value))
        else:
            yield 'Run {} on {}??? Noooo. Testers will kill me.'.format(commands, sorted(host_list))

    @re_botcmd(pattern=r"(.*)(damn|fuck|stupid)(.*)$", flags=re.IGNORECASE)
    def be_nice(self, msg, match):
        yield "Could you be more nice (((?"

    @re_botcmd(pattern=r"(.*)(please)(.*)$", flags=re.IGNORECASE)
    def gracefull(self, msg, match):
        yield "Of course, here you are:"

    @re_botcmd(pattern=r"^show(.*)karaf(.*)(features|ftrs)(.*)$", flags=re.IGNORECASE)
    def karaf_features(self, msg, match):
        """Get info about karaf features versions"""
        host_list = KARAF_LIST
        commands = ["feature:info draas-proxy |head -n 1",
                    "feature:info carpathia-sync-service |head -n 1",
                    "feature:info ump-commons-feature |head -n 1",
                    "feature:info ump-roster-feature |head -n 1",]
        host_type = 'karaf'
        d = ExecMsgParams(host_list, commands, match, host_type).exec()
        for key, value in d.items():
            yield('Karaf on {} have features:'.format(key))
            v = str(value).split(',')
            for f in v:
                yield(f)



    @botcmd
    def tail_catalina(self, msg, args):
        """Get info about portal versions"""
        l = []
        for host in PORTAL_LIST:
            t = exec_remote(host, ["sudo tail -n 10 /home/tomcat/portal/logs/catalina.out"])
            yield "Getting logs from {}".format(host)
            l.append("tail catalina.out on %s : %s" % (host, t.exec()))
        yield '\n'.join(l)
