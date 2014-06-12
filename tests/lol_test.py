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

    def test_case_insensitive(self):
        nick('A').says('Something unfunny')
        nick('B').says('lol')
        nick('B').says('.lols a')
        self.shouldSay("B: A's hilarity ranking is 1")

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

        nick('Bob').says('.lols Cat')
        self.shouldSay("Bob: Cat is not funny.")

    def test_lol_record(self):
        nick('Art').says('a funny thing')
        self.__lols(5)
        nick('Art').says('a funnier thing')
        self.__lols(10)
        nick('Art').says('a funny thing')
        self.__lols(5)

        nick('Art').says('.chain')
        self.shouldSay("Art: Your record lol chain is 10, after saying " +
                       "'a funnier thing'")

    def __lols(self, number):
        for i in xrange(number):
            nick("Nick%d" % i).says("lol")
