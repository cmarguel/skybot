import unittest
import sqlite3
import Queue
import traceback
import inspect
import collections
import re
from core import irc
from core import main
from datetime import datetime

bot = None
conn = None
db = None
mock_time = None
mock_datetime_handler = None


def make_signature(f):
    return f.func_code.co_filename, f.func_name, f.func_code.co_firstlineno


def format_plug(plug, kind='', lpad=0, width=40):
    out = ' ' * lpad + '%s:%s:%s' % make_signature(plug[0])
    if kind == 'command':
        out += ' ' * (50 - len(out)) + plug[1]['name']

    if kind == 'event':
        out += ' ' * (50 - len(out)) + ', '.join(plug[1]['events'])

    if kind == 'regex':
        out += ' ' * (50 - len(out)) + plug[1]['regex']

    return out


def fake_reload(pluginToTest):
    bot.plugs = collections.defaultdict(list)
    bot.threads = {}

    # compile new plugins
    allFunctions = inspect.getmembers(pluginToTest)
    functions = [func[1] for func in allFunctions
                 if type(func[1]).__name__ == 'function']
    for func in functions:
        if hasattr(func, '_hook'):  # check for magic
            if func._thread:
                bot.threads[func] = FakeHandler(func)

            for kind, data in func._hook:
                bot.plugs[kind] += [data]

    # print '  plugin listing:'
    # print bot.plugs

    bot.commands = {}
    for plug in bot.plugs['command']:
        name = plug[1]['name'].lower()
        bot.commands[name] = plug

    bot.events = collections.defaultdict(list)
    for func, args in bot.plugs['event']:
        for event in args['events']:
            bot.events[event].append((func, args))

    if bot.commands:
        # hack to make commands with multiple aliases
        # print nicely

        # print '    command:'
        commands = collections.defaultdict(list)

        for name, (func, args) in bot.commands.iteritems():
            commands[make_signature(func)].append(name)

        for sig, names in sorted(commands.iteritems()):
            names.sort(key=lambda x: (-len(x), x))  # long names first
            out = ' ' * 6 + '%s:%s:%s' % sig
            out += ' ' * (50 - len(out)) + ', '.join(names)
            # print out

    for kind, plugs in sorted(bot.plugs.iteritems()):
        if kind == 'command':
            continue
        # print '    %s:' % kind
        # for plug in plugs:
            # print format_plug(plug, kind=kind, lpad=6)
    # print


class FakeHandler(object):

    '''Runs plugins in their own threads (ensures order)'''

    def __init__(self, func):
        self.func = func
        self.input_queue = Queue.Queue()

    def start(self):
        pass

    def handle(self, value):
        global db
        uses_db = 'db' in self.func._args

        if uses_db:
            value.db = db

        try:
            main.run(self.func, value)
        except:
            traceback.print_exc()

    def stop(self):
        self.input_queue.put(StopIteration)

    def put(self, value):
        self.input_queue.put(value)
        self.handle(value)


class FakeBot():

    def __init__(self):
        self.conns = {}
        self.threads = {}
        self.config = {}
        self.persist_dir = ""

        self.thoughts = []


class TestIRC(irc.IRC):

    def __init__(self):
        self.set_conf({'nick': 'skybot', 'server': 'testirc.testirc.net'})
        self.out = Queue.Queue()  # responses from the server are placed here
        self.thoughts = []

    def cmd(self, command, params=None):
        pass

    def msg(self, chan, msg):
        bot.thoughts += [(chan, msg)]


def construct_out_params(nick='buttbot', msg='butts', chan='#test'):
    prefix = ":%s!~%s@butts.buttbutt.buttbutt.IP" % (nick, nick)
    params = "%s :%s" % (chan, msg)
    return ["%s PRIVMSG %s" % (prefix, params),
            prefix, 'PRIVMSG', params, nick, nick,
            'butts.buttbutt.buttbutt.IP',
            [chan, msg], msg]


class Nick:

    def __init__(self, nick):
        self.nick = nick

    def says(self, msg):
        out = construct_out_params(self.nick, msg)
        main.main(conn, out)


class MockTime(object):

    def __init__(self):
        self.curr_time = 1000000000.000

    def time(self):
        return self.curr_time


class MockDateTimeHandler(object):

    def __init__(self, moduleWithTimeSince=None):
        self.module = moduleWithTimeSince

    def update(self, timestamp):
        if self.module.timesince:
            mock_datetime = datetime.fromtimestamp(mock_time.time())
            self.module.timesince.timesince.__defaults__ = (mock_datetime,)


class PluginTest(unittest.TestCase):

    def setUp(self, module):
        bot.thoughts = []

        self.__prepare_plugins(module)
        self.__mock_time(module)

    def __prepare_plugins(self, module):
        allFunctions = inspect.getmembers(module)
        functions = [func[1] for func in allFunctions
                     if type(func[1]).__name__ == 'function']
        for func in functions:
            if hasattr(func, '_hook'):  # check for magic
                func._thread = True
                bot.threads[func] = FakeHandler(func)
        fake_reload(module)

    def __mock_time(self, module):
        global mock_datetime_handler

        module.time = mock_time
        if module.timesince:
            mock_datetime_handler = MockDateTimeHandler(module)
        else:
            mock_datetime_handler = MockDateTimeHandler()
        mock_time.curr_time = 1000000000.000

        mock_datetime_handler.update(mock_time.curr_time)

    def shouldSay(self, expectedMessage):
        thought = bot.thoughts.pop(0)
        if thought[1] == expectedMessage:
            return True

        self.fail("Skybot didn't respond with '%s'; got '%s'" %
                  (expectedMessage, thought[1]))

    def shouldBeSilent(self):
        if len(bot.thoughts) > 0:
            self.fail("Bot shouldn't respond, but was thinking all of this: %s"
                      % (bot.thoughts))

    def shouldPM(self, expectedRecipient, expectedMessage):
        thought = bot.thoughts.pop(0)
        if thought[0] == expectedRecipient and thought[1] == expectedMessage:
            return True
        self.fail("Skybot is supposed to tell %s '%s'; instead told %s '%s'" %
                  (expectedRecipient, expectedMessage, thought[0], thought[1]))


def setUpModule():
    global db, bot, conn, mock_time, mock_datetime
    db = sqlite3.connect(":memory:")
    bot = FakeBot()
    bot.get_db_connection = lambda x, y: db
    main.bot = bot
    main.re = re
    conn = TestIRC()
    mock_time = MockTime()
    mock_datetime = datetime.fromtimestamp(mock_time.time())


def nick(nick):
    return Nick(nick)


def after(period, units="minutes"):
    table = {
        'microseconds': 0.001,
        'seconds': 1.,
        'minutes': 60,
        'hours': 60 * 60,
        'days': 60 * 60 * 24,
        'weeks': 60 * 60 * 24 * 7,
        'months': 60 * 60 * 24 * 30,
        'years': 60 * 60 * 24 * 365
    }
    if units not in table:
        units = "minutes"
    mock_time.curr_time += period * table[units]
    mock_datetime_handler.update(mock_time.curr_time)
