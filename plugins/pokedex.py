from util import hook, http
import re


def db_init(db):
    "check to see that our db has the the pokedex table and return"
    " a connection."

    db.execute("create table if not exists pokedex("
               "id, name, language, version, flavor, "
               "primary key(id))")
    db.commit()


def cache(db, id, name, language, version, flavor):
    db.execute("insert or replace into pokedex("
               "id, name, language, version, flavor)"
               "values(?,?,?,?,?)", (id, name, language, version, flavor))
    db.commit()


def get(db, query, language, version):
    row = db.execute("select flavor from pokedex where "
                     "(id=? or name=? collate nocase) and "
                     "language=? and version=?",
                     (query, query, language, version)).fetchone()
    if row:
        return row[0]
    else:
        return None


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

    flavor = get(db, query, requested_language, requested_version)
    if flavor is not None:
        return flavor

    try:
        entry = http.get_json(base_url + query)

        return extract_text(db, entry, requested_language, requested_version)
    except http.HTTPError:
        return "Missingno"


def extract_text(db, entry, requested_language, requested_version):
    entries = entry['flavor_text_entries']
    name = extract_name(entry, requested_language)
    for flavor_entry in entries:
        language = flavor_entry["language"]["name"]
        version = flavor_entry["version"]["name"]
        if version == requested_version and requested_language == language:
            flavor = flavor_entry["flavor_text"].replace('\n', ' ')
            cache(db, entry["id"], name, language, version, flavor)
            return flavor
    return "Missingno"


def extract_name(entry, requested_language):
    names = entry['names']
    for name in names:
        language = name["language"]["name"]
        if language == requested_language:
            return name["name"]
    return "Missingno"
