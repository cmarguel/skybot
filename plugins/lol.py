# -*- coding: utf-8 -*-

from util import hook, munge

last_seen = None
last_quote = None
streak = 0


def db_init(db):
    "check to see that our db has the the lols table and return a connection."
    db.execute("create table if not exists lols(name, score, record, quote, "
               "primary key(name))")
    Person.set_db(db)
    db.commit()


@hook.singlethread
@hook.event('PRIVMSG', ignorebots=True)
def seeninput(paraml, input=None, db=None, bot=None):
    global last_seen, streak, last_quote

    db_init(db)

    msg = input.msg
    nick = input.nick

    target = last_seen

    if get_parts_if_direct_lol(msg) is not None:
        t, m = get_parts_if_direct_lol(msg)
        if target_is_chatter(t):
            target, msg = t, m

    if is_lol(msg):
        if target.lower() != nick.lower():
            person = Person.get(target)
            person.score += 1
            streak += 1
            if person.record <= streak:
                person.record = streak
                person.quote = last_quote
            person.save()
    elif is_memorable(nick, msg):
        last_seen = nick
        last_quote = msg
        streak = 0


def target_is_chatter(nick):
    return Person.get(nick) is not None

# Examples of not memorable things: lol, bot commands?


def is_memorable(nick, msg):
    return not is_lol(msg)


def is_lol(msg):
    lols = ['lol', 'lmao', 'lols', 'lolz']
    if msg.strip() in lols:
        return True
    return False


def get_parts_if_direct_lol(msg):
    parts = msg.split(" ")

    if len(parts) == 2:
        if parts[0][-1] in [':', ','] and is_lol(parts[1]):
            return parts[0][:-1], parts[1]
        elif is_lol(parts[0]):
            return parts[1], parts[0]
        else:
            return None
    else:
        return None

def retrieve_top_lollers(db, toplollercount=5):
    db_init(db)

    results = db.execute("SELECT name, score FROM lols ORDER BY score DESC").fetchmany(size=toplollercount)
    ret = ""
    rank = 1
    for pair in results:
        user, score = pair
        ret += "#%d %s:%d | " % (rank, munge.munge(user, 1), score)
        rank += 1
    return ret[:-3]


@hook.command
def lols(inp, nick='', chan='', db=None, input=None):
    db_init(db)

    thirdPerson = False
    if inp is not None and inp.strip() != "":
        nick = inp
        thirdPerson = True

    person = Person.get(nick)
    return person.describe_score(thirdPerson)


@hook.command
def chain(inp, nick='', chan='', db=None, input=None):
    db_init(db)

    thirdPerson = False
    if inp is not None and inp.strip() != "":
        nick = inp
        thirdPerson = True

    person = Person.get(nick)
    return person.describe_record(thirdPerson)

@hook.command
def toplols(inp, nick='', chan='', db=None, input=None):
    db_init(db)

    return retrieve_top_lollers(db)




class Person(object):

    @classmethod
    def set_db(cls, db):
        cls.db = db

    @classmethod
    def get(cls, nick):
        nick = nick.strip('_').split('|')[0]
        params = cls.db.execute("select name, score, record, quote from lols\
                                 where name = ? collate nocase", (nick,)).\
            fetchone()
        if params is None:
            return Person((nick, 0, 0, None))
        else:
            return Person(params)

    def __init__(self, tup):
        name, score, record, quote = tup
        self.name = name.strip('_').split('|')[0]
        self.score = score
        self.record = record
        self.quote = quote

    def to_tuple(self):
        return (self.name, self.score, self.record, self.quote)

    def save(self):
        Person.db.execute("insert or replace into lols(name, score, record, \
                        quote) values(?,?,?,?)", (self.to_tuple()))
        Person.db.commit()

    def describe_score(self, thirdPerson=False):
        if self.score == 0 and thirdPerson:
            return "%s is not funny." % self.name
        elif self.score == 0 and not thirdPerson:
            return "You're not funny."
        elif thirdPerson:
            return "%s's hilarity ranking is %d" % (self.name, self.score)
        else:
            return "Your hilarity ranking is %d" % self.score

    def describe_record(self, thirdPerson=False):
        if self.record == 0 and thirdPerson:
            return "%s is not funny." % self.name
        elif self.record == 0 and not thirdPerson:
            return "You're not funny."
        elif thirdPerson:
            return "%s's record lol chain is %d, after saying '%s'" % \
                (self.name, self.record, self.quote)
        else:
            return "Your record lol chain is %d, after saying '%s'" % \
                (self.record, self.quote)
