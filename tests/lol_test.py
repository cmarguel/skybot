import plugin_test
import plugins.lol
from plugin_test import *


class SeenTest(plugin_test.PluginTest):

    def setUp(self):
        plugin_test.PluginTest.setUp(self, plugins.lol)

    def test_no_change_if_lol_is_first_message_seen(self):
        nick('A').says('lol')
        nick('A').says('.lols')
        self.shouldSay("A: You're not funny.")

    def test_no_change_if_lol_query_is_first_message_seen(self):
        nick('A').says('.lols')
        self.shouldSay("A: You're not funny.")

    def test_lol_score_accumulates(self):
        nick('A').says('funny thing')
        nick('B').says('lol')
        nick('A').says('.lols')
        self.shouldSay("A: Your hilarity ranking is 1")

        nick('A').says('another funny thing')
        nick('B').says('lol')
        nick('C').says('lol')
        nick('A').says('.lols')
        self.shouldSay("A: Your hilarity ranking is 3")

    def test_cannot_lol_self(self):
        nick('A').says('Something unfunny')
        nick('A').says('lol')
        nick('A').says('.lols')
        self.shouldSay("A: You're not funny.")

    def test_lols_with_whitespace(self):
        nick('A').says('funny thing')
        nick('B').says(' lol ')
        nick('A').says('.lols')
        self.shouldSay("A: Your hilarity ranking is 1")

    def test_track_other_people_lols(self):
        nick('Art').says('another funny thing')
        nick('Bob').says('lol')
        nick('Cat').says('lol')
        nick('Bob').says('.lols Art')
        self.shouldSay("Bob: Art's hilarity ranking is 2")
