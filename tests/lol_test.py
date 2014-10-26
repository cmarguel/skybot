import plugin_test
import plugins.lol
from plugin_test import *


class LolTest(plugin_test.PluginTest):

    def setUp(self):
        plugin_test.PluginTest.setUp(self, plugins.lol)
        self.mayMungeOutput()

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

    def test_direct_lol(self):
        nick('A').says('a funny thing')
        nick('B').says('a mundane thing')
        nick('C').says('A: lol')
        nick('D').says('lol a')

        nick('A').says('.lols')
        self.shouldSay('A: Your hilarity ranking is 2')

    def test_ignores_nick_variations(self):
        nick('Art').says('a funny thing')
        nick('B').says('lol')
        nick('__Art__').says('a funny thing')
        nick('B').says('lol')
        nick('Art|work').says('a funny thing')
        nick('B').says('lol')

        nick('Art').says('.lols')
        self.shouldSay('Art: Your hilarity ranking is 3')
        nick('__Art__').says('.lols')
        self.shouldSay('__Art__: Your hilarity ranking is 3')
        nick('Art|work').says('.lols')
        self.shouldSay('Art|work: Your hilarity ranking is 3')

    def test_top_lollers(self):
        init_table = [('Alfa', 1),
                      ('Bravo', 20),
                      ('Charlie', 40),
                      ('Delta', 60),
                      ('Echo', 70),
                      ('Foxtrot', 80),
                      ('Golf', 90),
                      ('Hotel', 100),
                      ('India', 200),
                      ('Juliet', 300),
                      ('Kilo', 300),
                      ('Lima', 300)]
        self.__multi_lols(init_table)
        nick("Dummy").says(".toplols")
        self.shouldSay("Dummy: #1 Juliet:300 | #2 Kilo:300 | #3 Lima:300 | #4 India:200 | #5 Hotel:100")
        nick("Juliet").says("wherefore art thou romeo")
        self.__lols(5)
        nick("Dummy").says(".toplols")
        self.shouldSay("Dummy: #1 Juliet:305 | #2 Kilo:300 | #3 Lima:300 | #4 India:200 | #5 Hotel:100")
        nick("Lima").says("hello butts")
        self.__lols(20)
        nick("Dummy").says(".toplols")
        self.shouldSay("Dummy: #1 Lima:320 | #2 Juliet:305 | #3 Kilo:300 | #4 India:200 | #5 Hotel:100")

    def __lols(self, number):
        for i in xrange(number):
            nick("Nick%d" % i).says("lol")

    #populate db with multiple lol counts for test_top_lollers
    # initial_table is a list of (NAME, LOL_COUNT) tuples
    def __multi_lols(self, initial_table):
        for t in initial_table:
            nick(t[0]).says('a funny thing')
            self.__lols(t[1])

