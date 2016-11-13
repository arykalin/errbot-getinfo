from errbot import BotPlugin, botcmd, arg_botcmd, webhook
import logging
from elasticsearch import Elasticsearch
from config import ELASTIC_SERVER
from tools import look_for_host_in_host_list
from config import KARAF_LIST
from config import PORTAL_LIST
from config import OPENAM_LIST

class e_search(object):
    def __init__(self, host, source, match, size=1):
        self.log = logging.getLogger("errbot.plugins.%s" % self.__class__.__name__)
        self.host = host
        self.source = source
        self.match = match
        self.size = size
    def exec(self):
        self.log.debug('host inventory in search {}'.format(self.host))
        es = Elasticsearch(ELASTIC_SERVER)
        our_q = {"from":0,"size":self.size,"query":{"bool":{"should":[{"match":{"host":self.host}}, {"match":{' \
                '"source":self.source}}, {"match":{"message":self.match+"*"}}]}}}
        res = es.search(index="logstash-*",body=our_q)
        print("Got %d Hits:" % res['hits']['total'])
        for hit in res['hits']['hits']:
            print("%(@timestamp)s %(host)s: %(message)s" % hit["_source"])

class Search(BotPlugin):
    """
    Make various searches
    """

    @arg_botcmd('host', type=str)
    @arg_botcmd('--size', dest='size', type=int, default=1)
    @arg_botcmd('--match', dest='match', type=str, default="ERROR")
    @arg_botcmd('--source', dest='source', type=str, default="catalina.out")
    def latest_erro(self, mess, host=None, size=None, match=None, source=None):
        yield("Searching logs from host "+host+" from "+source+" for match "+match+" with size "+str(size))
        s = e_search(host,source,match,size)
        yield s.exec()



