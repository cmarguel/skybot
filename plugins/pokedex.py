from util import hook, http
import re
import random


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
    return db.execute("select version, flavor from pokedex where "
                      "(id=? or name=? collate nocase) and "
                      "language=?",
                     (query, query, language)).fetchall()


@hook.command
@hook.command("dex")
def pokedex(inp, nick='', chan='', db=None, input=None):
    ".pokedex name|id"

    db_init(db)

    base_url = "http://pokeapi.co/api/v2/pokemon-species/"

    default_language = "en"
    default_version = "x"

    query = inp.lower()
    valid = re.match('^[\w-]+$', query) is not None

    if not valid:
        return "Missingno"

    requested_version = default_version
    requested_language = default_language

    flavors = get_flavors(db, query, requested_language)
    if flavors and len(flavors) > 1:
        rand = random.randint(0, len(flavors) - 1)
        return flavors[rand][1]

    try:
        entry = http.get_json(base_url + query)
        cache_flavors(db, entry, requested_language, requested_version)

        return get_random_flavor(db, query, requested_language)
    except http.HTTPError:
        return "Missingno"


def get_random_flavor(db, query, language):
    flavors = get_flavors(db, query, language)
    rand = random.randint(0, len(flavors) - 1)
    return flavors[rand][1]


def cache_flavors(db, entry, requested_language, requested_version):
    entries = entry['flavor_text_entries']
    name = extract_name(entry, requested_language)
    for flavor_entry in entries:
        language = flavor_entry["language"]["name"]
        version = flavor_entry["version"]["name"]
        if requested_language == language:
            flavor = flavor_entry["flavor_text"].replace('\n', ' ')
            cache(db, entry["id"], name, language, version, flavor)
            # return flavor
    return "Missingno"


def extract_name(entry, requested_language):
    names = entry['names']
    for name in names:
        language = name["language"]["name"]
        if language == requested_language:
            return name["name"]
    return "Missingno"
