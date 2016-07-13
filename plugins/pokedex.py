from util import hook, http
import re
import random
import sys


def db_init(db):
    "check to see that our db has the the pokedex table and return"
    " a connection."

    db.execute("create table if not exists pokedex("
               "id, name, language, version, flavor) ")
    db.commit()


def cache(db, id, name, language, version, flavor):
    db.execute("insert or replace into pokedex("
               "id, name, language, version, flavor)"
               "values(?,?,?,?,?)", (id, name, language, version, flavor))
    db.commit()


def get_flavors(db, query, language):
    return db.execute("select id, name, version, flavor from pokedex where "
                      "(id=? or name=? collate nocase) and "
                      "language=?",
                     (query, query, language)).fetchall()


@hook.command
@hook.command("dex")
def pokedex(inp, nick='', chan='', db=None, input=None):
    "!pokedex name|id"

    db_init(db)

    reload(sys)
    sys.setdefaultencoding('utf8')

    base_url = "http://pokeapi.co/api/v2/pokemon-species/"

    default_language = "en"
    default_version = "x"

    query = asciify(inp.lower())
    valid = re.match('^[\w-]+$', query) is not None

    if not valid:
        return "A wild Missingno appeared!"

    requested_version = default_version
    requested_language = default_language

    flavor = get_random_flavor(db, query, requested_language)
    if flavor:
        return flavor

    try:
        entry = http.get_json(base_url + query)
        cache_flavors(db, entry, requested_language, requested_version)

        return get_random_flavor(db, query, requested_language)
    except http.HTTPError:
        return "A wild Missingno appeared!"


def get_random_flavor(db, query, language):
    flavors = get_flavors(db, query, language)
    if flavors:
        rand = random.randint(0, len(flavors) - 1)

        prelude = "#%s %s - " % (flavors[rand][0], flavors[rand][1])
        post = " (%s)" % flavors[rand][2]

        return prelude + flavors[rand][3] + post
    else:
        return None


def cache_flavors(db, entry, requested_language, requested_version):
    entries = entry['flavor_text_entries']
    # name = extract_name(entry, requested_language)
    for flavor_entry in entries:
        language = flavor_entry["language"]["name"]
        version = flavor_entry["version"]["name"]
        if requested_language == language:
            flavor = asciify(flavor_entry["flavor_text"])
            cache(db, entry["id"], entry["name"], language, version, flavor)
            # return flavor
    return "A wild Missingno appeared!"


def asciify(s):
    flavor = s.encode('utf-8').strip()
    flavor = flavor.replace('\xa9', '')
    flavor = flavor.replace('\xe9', 'e')
    flavor = flavor.replace('\xc3', 'e')
    flavor = flavor.replace('\xad', '')
    flavor = flavor.replace('\f', ' ')
    flavor = flavor.replace('\n', ' ')
    flavor = flavor.replace(u'\u2019', '\'')
    flavor = flavor.replace(u'\u2642', '(m)')
    flavor = flavor.replace(u'\u2640', '(f)')
    filtered = ""
    for c in flavor:
        if ord(c) < 128:
            filtered += c

    return filtered.encode('ascii')


def extract_name(entry, requested_language):
    names = entry['names']
    for name in names:
        language = name["language"]["name"]
        if language == requested_language:
            return asciify(name["name"])
    return "A wild Missingno appeared!"
