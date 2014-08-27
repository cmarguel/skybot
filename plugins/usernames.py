"usernames.py - For remembering other IRC users' usernames for things"

from util import hook


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


@hook.command
def username(inp, nick='', chan='', db=None, input=None):
    db_init(db)
    nick = nick.lower()

    args = inp.split(" ", 1)

    if len(args) == 1:
        return __lookup(nick, chan, args[0], db)
    else:
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
