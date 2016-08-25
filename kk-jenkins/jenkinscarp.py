from errbot import BotPlugin, botcmd, arg_botcmd, webhook
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
        
        self.send(msg.frm, u"/me is starting 'versions' job in Jenkins... ")
        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        self.jenkins.build_job('versions')
        
        return "Jenkins job 'versions' started"

    @botcmd
    def j_list(self, mess, args):
        """List all jobs, optionally filter them using a search term."""
        self.send(mess.frm, u'/me is getting the list of jobs from Jenkins... ')
                        
        search_term = args.strip().lower()
        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        jobs = [inst for job,inst in self.jenkins.get_jobs() if search_term.lower() in inst.name.lower()]
                                        
        return self.format_jobs(jobs)

    @botcmd(admin_only=True)
    def j_run(self, msg, args):
        """A command which starts Jenkins job given as parameter"""
        
        job_name = args.strip()
        self.send(msg.frm, u"/me is starting job in Jenkins... ")
        self.jenkins = Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)
        self.jenkins.build_job(job_name)
        
        return "Jenkins job '"+job_name+"' started"


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


#    @arg_botcmd('name', type=str)
#    @arg_botcmd('--favorite-number', type=int, unpack_args=False)
#    def hello(self, message, args):
#        """
#        A command which says hello to someone.
#
#        If you include --favorite-number, it will also tell you their
#        favorite number.
#        """
#        if args.favorite_number is None:
#            return "Hello {name}".format(name=args.name)
#        else:
#            return "Hello {name}, I hear your favorite number is {number}".format(
#                name=args.name,
#                number=args.favorite_number,
#            )
