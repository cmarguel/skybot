import unittest
import sqlite3
import Queue
import traceback
import inspect
import collections
import re
from core import irc
from core import main

bot = None
conn = None
db = None


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
        #for plug in plugs:
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


class Nick:

    def __init__(self, nick):
        self.nick = nick

    def says(self, msg):
        # out = [u':Argue!~Argue___@1D5EB980.CB99A000.75626F1E.IP PRIVMSG
        # lloidtest :foobar',
        # u':Argue!~Argue___@1D5EB980.CB99A000.75626F1E.IP', u'PRIVMSG',
        # u'#lloidtest :foobar', u'Argue', u'~Argue___',
        # u'1D5EB980.CB99A000.75626F1E.IP', [u'#lloidtest', u'foobar'],
        # u'foobar']
        out = [msg, 'prefix', 'PRIVMSG', 'params', self.nick, 'user', 'host',
               ['#chan_name', msg], msg]
        main.main(conn, out)


class PluginTest(unittest.TestCase):

    def setUp(self):
        pass

    def preparePlugins(self, module):
        allFunctions = inspect.getmembers(module)
        functions = [func[1] for func in allFunctions
                     if type(func[1]).__name__ == 'function']
        for func in functions:
            if hasattr(func, '_hook'):  # check for magic
                func._thread = True
                bot.threads[func] = FakeHandler(func)
        fake_reload(module)

                # for kind, data in func._hook:
                #    bot.plugs[kind] += [data]
                #
                # print '### new plugin (type: %s) loaded:' % \
                #        kind, reload.format_plug(data)

    def shouldSay(self, expectedMessage):
        for thought in bot.thoughts:
            if thought[1] == expectedMessage:
                return True
        if len(bot.thoughts) == 1:
            response = bot.thoughts[0][1]
        self.fail("Skybot didn't respond with '%s'; got '%s'" %
                  (expectedMessage, response))


def setUpModule():
    global db, bot, conn
    db = sqlite3.connect(":memory:")
    bot = FakeBot()
    bot.get_db_connection = lambda x, y: db
    main.bot = bot
    main.re = re
    conn = TestIRC()


def nick(nick):
    return Nick(nick)
