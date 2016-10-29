import sys
import paramiko

from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd, webhook

import logging
logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)

from config import SSH_KEY
from config import SSH_USER

class exec_remote(object):
    def __init__(self, hostname, commands):
        self.hostname = hostname
        self.commands = commands

    def exec(self):
        k = paramiko.RSAKey.from_private_key_file(SSH_KEY)
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logging.info("connecting")
        c.connect(self.hostname, username=SSH_USER, pkey=k)
        logging.info("Commands are {}".format(self.commands))
        l = []
        for command in self.commands:
            logging.info("Executing {}".format(command))
            stdin, stdout, stderr = c.exec_command(command, get_pty=True)
            for line in stdout:
                line = line.rstrip()
                l.append(line)

        c.close()

        #return ', '.join( repr(e).strip() for e in l)
        return ', '.join( repr(e) for e in l)


#portal_version = exec_remote("dev-test-app01.carpathia.com", ["sudo cat
# /home/tomcat/portal/webapps/portal/WEB-INF/release.properties|sed 's/.*=//'"])
#print(portal_version.exec())
#
# for i in range(1, 6):
#     host = "dev-test-app0" + str(i) + ".carpathia.com"
#     portal_version = exec_remote(host, ["sudo cat /home/tomcat/portal/webapps/portal/WEB-INF/release.properties|sed "
#                                      "'s/.*=//'"])
#     print("Portal version on %s : %s" % (host, portal_version.exec()), end='\n')
#
# log_tail = exec_remote("dev-test-app01.carpathia.com", ["sudo tail -n 1 /var/log/messages", "sudo uname -a"])
# print(log_tail.exec())

#   echo -n "OpenAM used on $host : "
#  grep ^com.iplanet.am.naming.url /home/tomcat/forgerock/j2ee_agents/tomcat_v6_agent/Agent_001/config/OpenSSOAgentBootstrap.properties
# --
#   echo -n "OpenAM version on ${host} : "
#  grep  urlArgs.*v /home/openam/forgerock/openam-tomcat/webapps/openam/XUI/index.html |sed -e 's/.*=//' -e 's/\".*//'
# --
#   echo -n "OpenAM DB used on ${host} : "
#  grep jdbc:postgresql /home/openam/forgerock/openam-tomcat/conf/context.xml|tail -n 1|sed 's#.*postgresql://##'
# --
#   echo -n "Space report on ${host} : "
#  df -h|grep /$

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
        for s in l:
            yield s

    @botcmd
    def portal_databases(self, msg, args):
        """Get info about portal versions"""
        l = []
        for h in range(1, 7):
            host = "dev-test-app0" + str(h) + ".carpathia.com"
            portal_database = exec_remote(host, ["sudo grep ^jdbc.mmdb.url /home/tomcat/portal/webapps/portal/WEB-INF/env.properties|sed 's#.*=.*jdbc:postgresql://##'"])
            l.append("Portal database used on %s : %s" % (host, portal_database.exec()))
        for s in l:
            yield s

    @botcmd
    def openam_versions(self, msg, args):
        """Get info about portal versions"""
        l = []
        for h in range(1, 7):
            host = "dev-test-openam0" + str(h) + ".carpathia.com"
            openam_version = exec_remote(host, ["sudo grep  urlArgs.*v ""/home/openam/forgerock/openam-tomcat/webapps/openam/XUI/index.html |sed -e 's/.*=//' -e 's/\".*//'"])
            l.append("OpenAM version on %s : %s" % (host, openam_version.exec()))
        for s in l:
            yield s

    @botcmd
    def tail_catalina(self, msg, args):
        """Get info about portal versions"""
        l = []
        for h in range(1, 7):
            host = "dev-test-app0" + str(h) + ".carpathia.com"
            t = exec_remote(host, ["sudo tail -n 10 /home/tomcat/portal/logs/catalina.out"])
            l.append("tail catalina.out on %s : %s" % (host, t.exec()))
        for s in l:
            yield s

    @re_botcmd(pattern=r"^(([Cc]an|[Mm]ay) I have a )?cookie please\?$")
    def hand_out_cookies(self, msg, match):
        """
        Gives cookies to people who ask me nicely.

        This command works especially nice if you have the following in
        your `config.py`:

        BOT_ALT_PREFIXES = ('Err',)
        BOT_ALT_PREFIX_SEPARATORS = (':', ',', ';')

        People are then able to say one of the following:

        Err, can I have a cookie please?
        Err: May I have a cookie please?
        Err; cookie please?
        """
        yield "Here's a cookie for you, {}".format(msg.frm)
        yield "/me hands out a cookie."