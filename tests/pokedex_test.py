import plugin_test
import plugins.pokedex
from plugin_test import *


class PokedexTest(plugin_test.PluginTest):

    def setUp(self):
        plugin_test.PluginTest.setUp(self, plugins.pokedex)

    # TODO: Now that it returns a random dex entry, this test doesn't work
    def test_pokedex_basic(self):
        nick("Ash").says(".pokedex pikachu")
        #self.shouldSay(
        #    "Ash: It raises its tail to check its surroundings."
        #    " The tail is sometimes struck by lightning in this pose.")

    def test_pokedex_not_found(self):
        nick("Ash").says(".pokedex missingno")
        self.shouldSay("Ash: Missingno")

    def test_invalid_pokemon(self):
        nick("Ash").says(".pokedex pika pika pi")
        self.shouldSay("Ash: Missingno")

    def x_test_caching(self):
        print "Ash is asking now."
        nick("Ash").says(".pokedex pikachu")
        print "Brock is asking now."
        nick("Brock").says(".pokedex pikachu")
        print "Done."
