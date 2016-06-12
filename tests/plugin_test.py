# -*- coding: utf-8 -*-

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


def reset_db():
    global bot, db
    bot.get_db_connection(None, None).close()
    db = sqlite3.connect(":memory:")
    bot.get_db_connection = lambda x, y: db


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
        self.conn = ()
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

    def pms(self, msg):
        out = construct_out_params(self.nick.lower(), msg, self.nick.lower())
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
        reset_db()

        self.__may_munge = False
        self.__prepare_plugins(module)
        if hasattr(module, 'timesince'):
            self.__mock_time(module)

    def mayMungeOutput(self):
        self.__may_munge = True

    def __resembles(self, a, b):
        if a == b:
            return True
        if a in character_replacements:
            return unicode(character_replacements[a]) == unicode(b)
        if b in character_replacements:
            return unicode(character_replacements[b]) == unicode(a)
        return False

    def __maybe_munged_equal(self, a, b):
        if len(a) != len(b):
            return False
        for i in xrange(len(a)):
            c = a[i]
            d = b[i]

            if c != d and not self.__resembles(c, d):
                return False
        return True

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

        if hasattr(module, 'time'):
            module.time = mock_time
        if hasattr(module, 'timesince'):
            mock_datetime_handler = MockDateTimeHandler(module)
        else:
            mock_datetime_handler = MockDateTimeHandler()
        mock_time.curr_time = 1000000000.000

        mock_datetime_handler.update(mock_time.curr_time)

    def shouldSay(self, expectedMessage):
        if len(bot.thoughts) == 0:
            self.fail("Skybot remained silent, but he should have said: %s" %
                      expectedMessage)
            return
        thought = bot.thoughts.pop(0)
        if (not self.__may_munge) and thought[1] == expectedMessage:
            return True
        if self.__may_munge and \
                self.__maybe_munged_equal(thought[1], expectedMessage):
            return True

        self.fail("Skybot didn't respond with '%s'; got '%s'" %
                  (expectedMessage, thought[1]))

    def shouldBeSilent(self):
        if len(bot.thoughts) > 0:
            self.fail("Bot shouldn't respond, but was thinking all of this: %s"
                      % (bot.thoughts))

    def shouldPM(self, expectedRecipient, expectedMessage):
        if len(bot.thoughts) == 0:
            self.fail("Skybot remained silent, but he should have sent \
                        %s this PM: %s" % (expectedRecipient, expectedMessage))
            return
        thought = bot.thoughts.pop(0)
        if thought[0].lower() == expectedRecipient.lower():
            if (not self.__may_munge) and thought[1] == expectedMessage:
                return True
            if self.__may_munge and \
                    self.__maybe_munged_equal(thought[1], expectedMessage):
                return True
        self.fail("Skybot is supposed to tell %s '%s'; instead told %s '%s'" %
                  (expectedRecipient, expectedMessage, thought[0], thought[1]))


def setUpModule():
    global db, bot, conn, mock_time, mock_datetime
    bot = FakeBot()
    db = sqlite3.connect(":memory:")
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

character_replacements = {
    'a': u'ä',
    #    'b': 'Б',
    'c': u'ċ',
    'd': u'đ',
    'e': u'ë',
    'f': u'ƒ',
    'g': u'ġ',
    'h': u'ħ',
    'i': u'í',
    'j': u'ĵ',
    'k': u'ķ',
    'l': u'ĺ',
    #    'm': 'ṁ',
    'n': u'ñ',
    'o': u'ö',
    'p': u'ρ',
    #    'q': 'ʠ',
    'r': u'ŗ',
    's': u'š',
    't': u'ţ',
    'u': u'ü',
    #    'v': '',
    'w': u'ω',
    'x': u'χ',
    'y': u'ÿ',
    'z': u'ź',
    'A': u'Å',
    'B': u'Β',
    'C': u'Ç',
    'D': u'Ď',
    'E': u'Ē',
    #    'F': 'Ḟ',
    'G': u'Ġ',
    'H': u'Ħ',
    'I': u'Í',
    'J': u'Ĵ',
    'K': u'Ķ',
    'L': u'Ĺ',
    'M': u'Μ',
    'N': u'Ν',
    'O': u'Ö',
    'P': u'Р',
    #    'Q': 'Ｑ',
    'R': u'Ŗ',
    'S': u'Š',
    'T': u'Ţ',
    'U': u'Ů',
    #    'V': 'Ṿ',
    'W': u'Ŵ',
    'X': u'Χ',
    'Y': u'Ỳ',
    'Z': u'Ż'}
