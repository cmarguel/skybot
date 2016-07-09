from util import hook, http
import re


@hook.command
def pokedex(inp, nick='', chan='', db=None, input=None):
    ".pokedex name|id"

    base_url = "http://pokeapi.co/api/v2/pokemon-species/"

    default_version = "x"

    query = inp.lower()
    valid = re.match('^[\w-]+$', query) is not None

    if not valid:
        return "Missingno"

    requested_version = default_version

    try:
        entry = http.get_json(base_url + query)

        return extract_text(entry, "en", requested_version)
    except http.HTTPError:
        return "Missingno"


def extract_text(entry, requested_language, requested_version):
    entries = entry['flavor_text_entries']
    for entry in entries:
        language = entry["language"]["name"]
        version = entry["version"]["name"]
        if version == requested_version and requested_language == language:
            return entry["flavor_text"].replace('\n', ' ')
