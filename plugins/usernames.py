# -*- coding: utf-8 -*-

"usernames.py - For remembering other IRC users' usernames for things"

from util import hook


def munge(inp, munge_count=0):
    reps = 0

    for n in xrange(len(inp)):
        rep = character_replacements.get(inp[n])
        if rep:
            inp = inp[:n] + unicode(rep) + inp[n + 1:]
            reps += 1
            if reps == munge_count:
                break
    return inp


def db_init(db):
    "check to see that our db has the the seen table and return a connection."
    db.execute("create table if not exists usernames("
               "name, chan, service, username, "
               "primary key(name, chan, service))")
    db.commit()


def __lookup(nick, chan, service, db):
    service = service.lower()

    username = db.execute("select username from usernames where"
                          " name=? and chan=? and service=?",
                          (nick, chan, service)).fetchone()

    if username is None:
        return "Your username for %s isn't registered" % service

    return 'Your %s username is "%s"' % (service, username[0])


def __insert(nick, chan, service, username, db):
    service = service.lower()

    db.execute("insert or replace into usernames(name,chan,service,username) "
               "values(?,?,?,?)",
               (nick, chan, service, username))
    db.commit()

    return 'Noted: You use %s as "%s"' % (service, username)


def __delete(nick, chan, service, db):
    db.execute("delete from usernames where name=? and chan=? and service=?",
               (nick, chan, service))
    db.commit()
    return "Okay, deleting your info for %s" % service


@hook.command
def gamer(inp, nick='', chan='', db=None, input=None):
    if inp is None or inp.strip() == "":
        return ".gamer gamename | .gamer gamename username | .gamer - gamename"
    db_init(db)
    nick = nick.lower()

    args = inp.split(" ", 1)

    if len(args) == 1:
        return __lookup(nick, chan, args[0], db)
    else:
        if args[0] == '-':
            return __delete(input.nick.lower(), input.chan, args[1], db)
        return __insert(input.nick.lower(), input.chan, args[0], args[1], db)


def __get_games(nick, chan, db):
    names = db.execute("select service, username from usernames where"
                       " name=? and chan=? order by lower(service)",
                       (nick, chan)).fetchall()
    if len(names) == 0:
        return None

    ret = ""
    for pair in names:
        service, username = pair
        ret += "%s: %s | " % (service, username)
    return ret[:-3]


def __get_usernames(chan, service, db):
    names = db.execute("select name, username from usernames where"
                       " chan=? and service=? order by lower(service)",
                       (chan, service)).fetchall()
    if len(names) == 0:
        return None

    ret = ""
    for pair in names:
        name, username = pair
        ret += "%s: %s | " % (name, username)
    return ret[:-3]


@hook.command
def gamers(inp, nick='', chan='', pm=None, db=None, input=None):
    db_init(db)
    if inp is None or inp.strip() == "":
        return None

    lookup = inp.lower()
    names = __get_usernames(chan, lookup, db)
    if names is None:
        return "Nobody seems to be playing that."
    pm('%s -> %s' % (lookup, names))


@hook.command
def games(inp, nick='', chan='', db=None, input=None):
    db_init(db)
    lookup = nick.lower()

    if len(inp) > 0:
        lookup = inp.lower()

    games = __get_games(lookup, chan, db)
    if nick.lower() == lookup:
        if games is None:
            return "You don't have any games registered."
        else:
            return games
    else:
        if games is None:
            return "%s has no games registered." % lookup
        else:
            return "%s -> %s" % (lookup, games)

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
