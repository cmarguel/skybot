import plugin_test
import plugins.pokedex
from plugin_test import *


class PokedexTest(plugin_test.PluginTest):

    def setUp(self):
        plugin_test.PluginTest.setUp(self, plugins.pokedex)

    def test_pokedex_basic(self):
        nick("Ash").says(".pokedex pikachu")
        self.shouldSay(
            "Ash: It raises its tail to check its surroundings."
            " The tail is sometimes struck by lightning in this pose.")

    def test_pokedex_not_found(self):
        nick("Ash").says(".pokedex missingno")
        self.shouldSay("Ash: Missingno")

    def test_invalid_pokemon(self):
        nick("Ash").says(".pokedex pika pika pi")
        self.shouldSay("Ash: Missingno")
