import sys
import paramiko
import re
import logging

from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd, webhook

#logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)

from config import SSH_KEY
from config import SSH_USER
host_dict = {'hostname': 'None'}
#TODO: Rewrite it to class exec_remote(BotPlugin):
# class GoogleCloud(BotPlugin):
#     def __init__(self, bot):
#         super().__init__(bot)
#         self.outdir = None
#         self.credentials = None
#         self.storage = None
#
#     """This is a common common for Google Cloud plugins."""
#
#     def activate(self):
#         super().activate()
#         self.outdir = self.bot_config.BOT_DATA_DIR
#https://github.com/GoogleCloudPlatform/err-stackdriver/blob/master/gcloud.py

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
    def __init__(self, host_list, commands, l, match):
        self.log = logging.getLogger("errbot.plugins.%s" % self.__class__.__name__)
        self.match = match
        self.host_list = host_list
        self.commands = commands
        self.l = l
    def exec(self):
        host_frm_msg = re.match("(.*)(\s+on\s+)(.*)", self.match.group(4))
        print(host_frm_msg)
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
                self.l.append("host {} not found in hosts list {}".format(host_frm_msg, self.host_list))
            else:
                # l.append("working with {}".format(host))
                openam_database = exec_remote(host, self.commands)
                self.l.append("OpenAM database used on {} : {}".format(host, openam_database.exec()))
        else:
            for host in self.host_list:
                # l.append('host is {}, going default: "OpenAM database used on {} :'.format(host_frm_msg,host))
                self.log.debug('host is {}, going default, checking database used on {} :'.format(host_frm_msg,host))
                openam_database = exec_remote(host, self.commands)
                self.l.append("OpenAM database used on {} : {}".format(host, openam_database.exec()))
        l = self.l
        return l

class GetInfo(BotPlugin):
    """Get info about environement"""

    @re_botcmd(pattern=r"^[Ss]how(.*)portal(.*)version(.*)$")
    def portal_versions(self, msg, args):
        """Get info about portal versions"""
        l = []
        for h in range(1, 7):
            host = "dev-test-app0" + str(h) + ".carpathia.com"
            portal_version = exec_remote(host, ["sudo cat /home/tomcat/portal/webapps/portal/WEB-INF/release.properties|sed "
                                             "'s/.*=//'"])
            l.append("Portal version on %s : %s" % (host, portal_version.exec()))
        yield '\n'.join(l)

    @re_botcmd(pattern=r"^[Ss]how(.*)portal(.*)(database|db)(.*)$", flags=re.IGNORECASE)
    def portal_databases(self, msg, args):
        """Get info about portal versions"""
        l = []
        for h in range(1, 7):
            host = "dev-test-app0" + str(h) + ".carpathia.com"
            portal_database = exec_remote(host, ["sudo grep ^jdbc.mmdb.url /home/tomcat/portal/webapps/portal/WEB-INF/env.properties|sed 's#.*=.*jdbc:postgresql://##'"])
            l.append("Portal database used on %s : %s" % (host, portal_database.exec()))
        yield '\n'.join(l)

    @re_botcmd(pattern=r"^[Ss]how(.*)openam(.*)version(.*)$", flags=re.IGNORECASE)
    def openam_versions(self, msg, args):
        """Get info about portal versions"""
        l = []
        for h in range(1, 7):
            host = "dev-test-openam0" + str(h) + ".carpathia.com"
            openam_version = exec_remote(host, ["sudo grep  urlArgs.*v ""/home/openam/forgerock/openam-tomcat/webapps/openam/XUI/index.html |sed -e 's/.*=//' -e 's/\".*//'"])
            l.append("OpenAM version on %s : %s" % (host, openam_version.exec()))
        yield '\n'.join(l)

    @re_botcmd(pattern=r"^show(.*)openam(.*)(database|db)(.*)$", flags=re.IGNORECASE)
    def openam_databases(self, msg, match):
        """Get info about portal versions"""
        l = []
        host_list = ["dev-test-openam01.carpathia.com","dev-test-openam02.carpathia.com","dev-test-openam03.carpathia.com"]
        commands = ["sudo grep jdbc:postgresql /home/openam/forgerock/openam-tomcat/conf/context.xml|tail -n 1|sed 's#.*postgresql://##'"]
        print("showing openam db")
        excmsg = ExecMsgParams(host_list, commands, l, match)
        print(excmsg.exec())
        yield excmsg.exec()

    @re_botcmd(pattern=r"^[Ss]how(.*)karaf(.*)(database|db)(.*)$", flags=re.IGNORECASE)
    def karaf_database(self, msg, args):
        """Get info about portal versions"""
        l = []
        hosts = ["dev-test-app01.carpathia.com",
                 "dev-test-app02.carpathia.com",
                 #"dev-test-microserv01.carpathia.com",
                 #"dev-test-microserv02.carpathia.com",
                 "dev-test-app05.carpathia.com",
                 "dev-test-app06.carpathia.com"]
        for h in hosts:
            host = h
            karaf_database = exec_remote_karaf(host, ["config:list|grep com.qts.ump.dao.db.name"])
            l.append("Karaf database property on %s : %s" % (host, karaf_database.exec()))
        yield '\n'.join(l)

    @botcmd
    def tail_catalina(self, msg, args):
        """Get info about portal versions"""
        l = []
        for h in range(1, 7):
            host = "dev-test-app0" + str(h) + ".carpathia.com"
            t = exec_remote(host, ["sudo tail -n 10 /home/tomcat/portal/logs/catalina.out"])
            yield "Getting logs from {}".format(host)
            l.append("tail catalina.out on %s : %s" % (host, t.exec()))
        yield '\n'.join(l)
