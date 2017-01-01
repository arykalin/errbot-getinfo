from tools import exec_remote
from tools import exec_remote_karaf
from errbot import BotPlugin, botcmd, re_botcmd, arg_botcmd, webhook




class GetInfo(BotPlugin):
    """Get info about environement"""
    @botcmd
    @arg_botcmd('host', type=str)
    # @re_botcmd(pattern=r"^show(.*)portal(.*)(version|vers)(.*)$")
    def getinfo_portal_versions(self, msg, host=None):
        """Get info about portal version"""
        commands = ["sudo cat /home/tomcat/portal/webapps/portal/WEB-INF/release.properties|sed 's/.*=//'"]
        m = exec_remote(host,commands).exec()
        yield('Portal version on {} : {}'.format(host, m))

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
    # @re_botcmd(pattern=r"^show(.*)portal(.*)(version|vers)(.*)$")
    def getinfo_widgets_versions(self, msg, host=None):
        """Get info about portal version"""
        commands = ["sudo cat /home/tomcat/portal/webapps/widget-incident/WEB-INF/classes/release.properties|sed 's/.*=/widget-incident : /'",
                    "sudo cat /home/tomcat/portal/webapps/widget-make-a-request/WEB-INF/classes/release.properties|sed 's/.*=/widget-make-a-request : /'",
                    "sudo cat /home/tomcat/portal/webapps/widget-my-assigned/WEB-INF/classes/release.properties|sed 's/.*=/widget-my-assigned : /'"]
        m = exec_remote(host,commands).exec()
        yield('Widgets version on {} : {}'.format(host, m))

    @botcmd
    @arg_botcmd('host', type=str)
    # @re_botcmd(pattern=r"^show(.*)portal(.*)(version|vers)(.*)$")
    def getinfo_power_versions(self, msg, host=None):
        """Get info about portal version"""
        commands = ["sudo cat /home/tomcat/portal/webapps/power/WEB-INF/classes/release.properties|sed 's/.*=//'"]
        m = exec_remote(host,commands).exec()
        yield('Power version on {} : {}'.format(host, m))

    @botcmd
    @arg_botcmd('host', type=str)
    # @re_botcmd(pattern=r"^show(.*)openam(.*)(version|vers)(.*)$", flags=re.IGNORECASE)
    def getinfo_openam_versions(self, msg, host=None):
        """Get info about openam version"""
        commands = ["sudo grep  urlArgs.*v ""/home/openam/forgerock/openam-tomcat/webapps/openam/XUI/index.html |sed -e 's/.*=//' -e 's/\".*//'"]
        m = exec_remote(host,commands).exec()
        yield('OpenAM version on {} : {}'.format(host, m))

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
                    "feature:info ump-roster-feature |head -n 1",
                    "feature:info servicenow-requests |head -n 1",
                    "feature:info qts-power-tool-feature |head -n 1"]
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

