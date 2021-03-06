import re
import logging
import paramiko

from config import SSH_KEY
from config import SSH_USER

class look_for_host_in_host_list(object):
    def __init__(self, host_regex, hosts_list):
        self.log = logging.getLogger("errbot.plugins.%s" % self.__class__.__name__)
        self.host_regex = host_regex
        self.hosts_list = hosts_list
    def search(self):
        r = re.compile('.*({}).*'.format(self.host_regex))
        self.log.debug("Looking for {} in {} with regex {}".format(self.host_regex,self.hosts_list,r))
        h = [m.group(0) for l in self.hosts_list for m in [r.search(l)] if m]
        #Making a set from list to remove dublicates
        hs = set(h)
        if hs.__len__() == 1:
            host = hs.pop()
            self.log.debug("{host_regex} match {host} in {list}".format(host_regex=self.host_regex,
                                                                     host=host,
                                                                     list=self.hosts_list))
            return host

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
        #TODO: rewrite to return norma text block
        #TODO: maybe convert list to tuple?
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
        #TODO: rewrite to return norma text block
        return ', '.join( repr(e) for e in l)
