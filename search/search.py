from errbot import BotPlugin, botcmd, arg_botcmd, webhook
import logging
from elasticsearch import Elasticsearch
from config import ELASTIC_SERVER

class search(object):
    def __init__(self, host):
        self.log = logging.getLogger("errbot.plugins.%s" % self.__class__.__name__)
        self.host = host
    def exec(self):
        self.log.debug('host inventory in search {}'.format(self.host))
        es = Elasticsearch(['http://dev-test-elk.carpathia.com:9200'])
        our_q = {"from":0,"size":1,"query":{"bool":{"should":[{"match":{"host":self.host}}, {"match":{' \
                '"source":"*catalina.out"}}, {"match":{"message":"ERROR*"}}]}}}
        res = es.search(index="logstash-*",body=our_q)
        print("Got %d Hits:" % res['hits']['total'])
        for hit in res['hits']['hits']:
            print("%(@timestamp)s %(host)s: %(message)s" % hit["_source"])

class Search(BotPlugin):
    """
    Make various searches
    """

    def activate(self):
        """
        Triggers on plugin activation

        You should delete it if you're not using it to override any default behaviour
        """
        super(Search, self).activate()

    def deactivate(self):
        """
        Triggers on plugin deactivation

        You should delete it if you're not using it to override any default behaviour
        """
        super(Search, self).deactivate()

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return {'EXAMPLE_KEY_1': "Example value",
                'EXAMPLE_KEY_2': ["Example", "Value"]
               }

    def check_configuration(self, configuration):
        """
        Triggers when the configuration is checked, shortly before activation

        Raise a errbot.utils.ValidationException in case of an error

        You should delete it if you're not using it to override any default behaviour
        """
        super(Search, self).check_configuration(configuration)

    def callback_connect(self):
        """
        Triggers when bot is connected

        You should delete it if you're not using it to override any default behaviour
        """
        pass

    def callback_message(self, message):
        """
        Triggered for every received message that isn't coming from the bot itself

        You should delete it if you're not using it to override any default behaviour
        """
        pass

    def callback_botmessage(self, message):
        """
        Triggered for every message that comes from the bot itself

        You should delete it if you're not using it to override any default behaviour
        """
        pass

    @webhook
    def example_webhook(self, incoming_request):
        """A webhook which simply returns 'Example'"""
        return "Example"

    # Passing split_args_with=None will cause arguments to be split on any kind
    # of whitespace, just like Python's split() does
    @botcmd(split_args_with=None)
    def example(self, message, args):
        """A command which simply returns 'Example'"""
        return "Example"

    @arg_botcmd('name', type=str)
    @arg_botcmd('--favorite-number', type=int, unpack_args=False)
    def hello(self, message, args):
        """
        A command which says hello to someone.

        If you include --favorite-number, it will also tell you their
        favorite number.
        """
        if args.favorite_number is None:
            return "Hello {name}".format(name=args.name)
        else:
            return "Hello {name}, I hear your favorite number is {number}".format(
                name=args.name,
                number=args.favorite_number,
            )

    @botcmd
    def latest_erro(self, msg, args):
        es = Elasticsearch(ELASTIC_SERVER)

        #our_q = '{"query":{"bool":{"should":[{"match":{"host":"dev-test-app05*"}},{"match":{"source":"*catalina.out"}}]}}}'
        #our_q = '{"query":{"bool":{"should":[{"match":{"host":"dev-test-app05*"}},{"match":{"source":"*catalina.out"}},
        # {"match":{"message":"ERROR*"}}]}}}'
        our_q = '{"from":0,"size":5,"query":{"bool":{"should":[{"match":{"host":"dev-test-app05*"}},{"match":{' \
                '"source":"*catalina.out"}},{"match":{"message":"ERROR*"}}]}}}'

        #res = es.search(index="logstash-2016.10.31",body=our_q)
        res = es.search(index="logstash-*",body=our_q)

        yield ("Got %d Hits:" % res['hits']['total'])

        for hit in res['hits']['hits']:
            yield ("%(@timestamp)s %(host)s: %(message)s" % hit["_source"])
