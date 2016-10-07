import json
import urllib.request
import random
import socket
import paramiko
import re

from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd, webhook
import jenkinsapi
from jenkinsapi.jenkins import Jenkins

from config import JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD

class Jenkinscarp(BotPlugin):
    """
    Jenkins CI integration for errbot
    """
    #def __init__(self,args):
    #    self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
#    @botcmd(admin_only=True)
                
    @botcmd(split_args_with=None)
    def j_vers(self, msg, args):
        """A command which simply starts 'versions' Jenkins job"""
        
#        self.send(msg.frm, u"/me is starting 'versions' job in Jenkins... ")
        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        self.jenkins.build_job('versions')
        
        return "Jenkins job 'versions' started"

    @botcmd
    def j_list(self, mess, args):
        """List all jobs, optionally filter them using a search term."""
#        yield  u'/me is getting the list of jobs from Jenkins... '
#        self.send(mess.frm, u'/me is getting the list of jobs from Jenkins... ')
                        
        search_term = args.strip().lower()
        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        Jjobs = self.jenkins.get_jobs()
        jobs = [inst for job,inst in Jjobs if search_term.lower() in inst.name.lower()]
                                        
        return self.format_jobs(jobs)

#    @botcmd(admin_only=True)
    @botcmd
    def j_run(self, msg, args):
        """A command which starts Jenkins job given as parameter"""
        
        job_name = args.strip()
#        self.send(msg.frm, u"/me is starting job in Jenkins... ")
        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        self.jenkins.build_job(job_name)
        
        return "Jenkins job '"+job_name+"' started"

    @botcmd(admin_only=True)
    def j_uatver(self, msg, args):
        """A command which sets UMP_VERSION_UAT global variable value"""
        
        uat_ver = args.strip()
        params = {'V_NAME': 'UMP_VERSION_UAT', 'V_VALUE': uat_ver }
        
        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        self.jenkins.build_job('set_global_var',params)
        
        return "Jenkins job 'set_global_var' started"

#    @botcmd(admin_only=True)
    @botcmd
    def j_deploy_sc(self, msg, args):
        """A command which starts Jenkins job wich deploys UMP to SC env with version given as parameter"""
        
        dp_ver = args.strip()
        params = {'DEPLOY_VER': dp_ver }
        
        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        self.jenkins.build_job('docker_ump_showcase',params)
        
        return "Jenkins job 'docker_ump_showcase' started"

#    @botcmd(admin_only=True)
    @botcmd
    def j_deploy_at(self, msg, args):
        """A command which starts Jenkins job wich deploys UMP to Autotest env with version given as parameter"""
        
        dp_ver = args.strip()
        params = {'DEPLOY_VER': dp_ver }
        
        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        self.jenkins.build_job('docker-ump-autotest',params)
        
        return "Jenkins job 'docker-ump-autotest' started"

    @botcmd
    def steve(self, msg, args):
        """A command which gets random image from last 20 photos in Steve's instagram"""
        
        with urllib.request.urlopen('https://www.instagram.com/fletcher_whiskeydog/media/') as response:
            js = response.read()
            
        resp = json.loads(js.decode("utf-8"))
        
        picnum = random.randrange(20)
        
        if args.strip().lower() == 'last':
            picnum = 0
        
        url  = resp['items'][picnum]['images']['standard_resolution']['url']

        return url
        
    @arg_botcmd('host', type=str)
    @arg_botcmd('cmdd', type=str)
    def openam(self, msg, cmdd='',host=''):
        """Usage: !openam start|stop|restart|status <host>"""
        hostname = host.strip().lower()
        if len(hostname) == 0:
            yield "No host name given. Usage: !portal start|stop|status|restart <hostname>"
            return

        cmd = cmdd.strip().lower()
        if cmd not in ['start','stop','status','restart']:
            yield "Invalid command given. Usage: !openam start|stop|status|restart <hostname>"
            return

        cmd = "systemctl " + cmd + " openam"
        yield "Will run '"+cmd+"' on host: "+self.run_cmd(hostname,"uname -n")
        yield self.run_cmd(hostname,cmd)
        
    @arg_botcmd('host', type=str)
    @arg_botcmd('cmdd', type=str)
    def portal(self, msg, cmdd='',host=''):
        """Usage: !portal start|stop|restart|status <host>"""
        hostname = host.strip().lower()
        if len(hostname) == 0:
            yield "No host name given. Usage: !portal start|stop|status|restart <hostname>"
            return

        cmd = cmdd.strip().lower()
        if cmd not in ['start','stop','status','restart']:
            yield "Invalid command given. Usage: !portal start|stop|status|restart <hostname>"
            return

        cmd = "systemctl " + cmd + " portal"
        yield "Will run '"+cmd+"' on host: "+self.run_cmd(hostname,"uname -n")
        yield self.run_cmd(hostname,cmd)

    @arg_botcmd('host', type=str)
    @arg_botcmd('cmdd', type=str)
    def karaf(self, msg, cmdd='',host=''):
        """Usage: !karaf start|stop|restart|status <host>"""
        hostname = host.strip().lower()
        if len(hostname) == 0:
            yield "No host name given. Usage: !karaf start|stop|status|restart <hostname>"
            return

        cmd = cmdd.strip().lower()
        if cmd not in ['start','stop','status','restart']:
            yield "Invalid command given. Usage: !karaf start|stop|status|restart <hostname>"
            return

        cmd = "systemctl " + cmd + " karaf"
        yield "Will run '"+cmd+"' on host: "+self.run_cmd(hostname,"uname -n")
        yield self.run_cmd(hostname,cmd)

#    @botcmd
#    def j_running(self, mess, args):
#        """List all running jobs."""
#        self.send(mess.frm, u'/me is getting the list of jobs from Jenkins... ')
#                        
#        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
#        jobs = [job for job,inst in self.jenkins.get_jobs() if inst.is_queued_or_running()]
#                                
#        return self.format_running_jobs(jobs)

    def format_jobs(self, jobs):
        if len(jobs) == 0:
            return u'No jobs found.'
                        
        max_length = max([len(job.name) for job in jobs])
        return '\n'.join(['%s (%s)' % (job.name.ljust(max_length), job.url) for job in jobs]).strip()

    def format_running_jobs(self, jobs):
        if len(jobs) == 0:
            return u'No running jobs.'
                        
        jobs_info = [self.jenkins.get_job_info(job['name']) for job in jobs]
        return '\n\n'.join(['%s (%s)\n%s' % (job['name'], job['lastBuild']['url'], job['healthReport'][0]['description']) for job in jobs_info]).strip()


    def run_cmd(self,hostname="dev-test-openam01",cmd="sudo systemctl status openam | grep Active"):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, 22))
        t = paramiko.Transport(sock)
        t.start_client()
        t.auth_publickey("ansible", paramiko.RSAKey.from_private_key_file("/etc/ansible/ansible.key"))
        chan = t.open_session()
        chan.exec_command(cmd)
        result = chan.recv(255).decode("utf-8")
        t.close()
        return result                            
                                    