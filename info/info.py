import sys
import paramiko
import select
import time
import logging
logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)

class exec_remote(object):
    def __init__(self, hostname, commands):
        self.hostname = hostname
        self.commands = commands

    def exec(self):
        k = paramiko.RSAKey.from_private_key_file("ansible.key")
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logging.info("connecting")
        c.connect(self.hostname, username="ansible", pkey=k)
        logging.info("Commands are {}".format(self.commands))
        l = []
        for command in self.commands:
            logging.info("Executing {}".format(command))
            stdin, stdout, stderr = c.exec_command(command, get_pty=True)
            r = stdout.read()
            e = stderr.read()
            l.append(r + e)

        c.close()
        return l


#portal_version = exec_remote("dev-test-app01.carpathia.com", ["sudo cat
# /home/tomcat/portal/webapps/portal/WEB-INF/release.properties|sed 's/.*=//'"])
#print(portal_version.exec())
#
for i in range(1, 6):
    host = "dev-test-app0" + str(i) + ".carpathia.com"
    portal_version = exec_remote(host, ["sudo cat /home/tomcat/portal/webapps/portal/WEB-INF/release.properties|sed "
                                     "'s/.*=//'", "sudo uname -a"])
    print("Portal version on %s : %s" % (host, portal_version.exec()))
#
# log_tail = exec_remote("dev-test-app01.carpathia.com", ["sudo tail -n 1 /var/log/messages", "sudo uname -a"])
# print(log_tail.exec())