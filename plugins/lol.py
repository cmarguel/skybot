from util import hook

last_seen = None


def db_init(db):
    "check to see that our db has the the lols table and return a connection."
    db.execute("create table if not exists lols(name, score, record, quote, "
               "primary key(name))")
    Person.set_db(db)
    db.commit()


@hook.singlethread
@hook.event('PRIVMSG', ignorebots=True)
def seeninput(paraml, input=None, db=None, bot=None):
    global last_seen

    db_init(db)

    msg = input.msg
    nick = input.nick

    if is_lol(msg):
        if last_seen != nick:
            person = Person.get(last_seen)
            person.score += 1
            person.save()

    elif is_memorable(nick, msg):
        last_seen = nick


def is_memorable(nick, msg):
    return not is_lol(msg)


def is_lol(msg):
    return msg.strip() == 'lol'


@hook.command
def lols(inp, nick='', chan='', db=None, input=None):
    db_init(db)

    return Person.get(nick).describe_score()


class Person(object):

    @classmethod
    def set_db(cls, db):
        cls.db = db

    @classmethod
    def get(cls, nick):
        params = cls.db.execute("select name, score, record, quote from lols\
                                 where name = ?", (nick,)).fetchone()
        if params is None:
            return Person((nick, 0, 0, None))
        else:
            return Person(params)

    def __init__(self, tup):
        name, score, record, quote = tup
        self.name = name
        self.score = score
        self.record = record
        self.quote = quote

    def to_tuple(self):
        return (self.name, self.score, self.record, self.quote)

    def save(self):
        Person.db.execute("insert or replace into lols(name, score, record, \
                        quote) values(?,?,?,?)", (self.to_tuple()))
        Person.db.commit()

    def describe_score(self):
        if self.score == 0:
            return "You're not funny."
        else:
            return "Your hilarity ranking is %d" % self.score
