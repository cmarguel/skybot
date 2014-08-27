import plugin_test
import plugins.usernames
from plugin_test import *


class UsernamesTest(plugin_test.PluginTest):

    def setUp(self):
        plugin_test.PluginTest.setUp(self, plugins.usernames)

    def test_add_username(self):
        nick('Art').says('.gamer steam')
        self.shouldSay("Art: Your username for steam isn't registered")

        nick('Art').says('.gamer steam art')
        self.shouldSay('Art: Noted: You use steam as "art"')

        nick('Art').says('.gamer steam')
        self.shouldSay('Art: Your steam username is "art"')

    def test_multiple_games(self):
        nick('Art').says('.games')
        self.shouldSay('Art: You don\'t have any games registered.')

        nick('Art').says('.gamer steam art1')
        self.shouldSay('Art: Noted: You use steam as "art1"')
        nick('Art').says('.gamer 3DS art2')
        self.shouldSay('Art: Noted: You use 3ds as "art2"')
        nick('Art').says('.gamer WiiU art3')
        self.shouldSay('Art: Noted: You use wiiu as "art3"')

        nick('Art').says('.games')
        self.shouldSay('Art: 3ds: art2 | steam: art1 | wiiu: art3')

        nick('Bob').says('.games art')
        self.shouldSay('Bob: art -> 3ds: art2 | steam: art1 | wiiu: art3')

    def test_lookup_users(self):
        nick('Dan').says('.gamers steam')
        self.shouldSay('Dan: Nobody seems to be playing that.')

        nick('Art').says('.gamer steam art')
        self.shouldSay('Art: Noted: You use steam as "art"')
        nick('Bob').says('.gamer steam bob')
        self.shouldSay('Bob: Noted: You use steam as "bob"')
        nick('Cat').says('.gamer steam cat')
        self.shouldSay('Cat: Noted: You use steam as "cat"')

        nick('Dan').says('.gamers steam')
        self.shouldSay('Dan: steam -> art: art | bob: bob | cat: cat')

    def test_delete(self):
        nick('Art').says('.gamer steam art1')
        self.shouldSay('Art: Noted: You use steam as "art1"')
        nick('Art').says('.gamer 3DS art2')
        self.shouldSay('Art: Noted: You use 3ds as "art2"')
        nick('Art').says('.gamer foobar baz')
        self.shouldSay('Art: Noted: You use foobar as "baz"')

        nick('Art').says('.games')
        self.shouldSay('Art: 3ds: art2 | foobar: baz | steam: art1')

        nick('Art').says('.gamer - 3ds')
        self.shouldSay('Art: Okay, deleting your info for 3ds')
        nick('Art').says('.gamer - foobar')
        self.shouldSay('Art: Okay, deleting your info for foobar')
        nick('Art').says('.games')
        self.shouldSay('Art: steam: art1')

    def test_help(self):
        nick('Art').says('.gamer')
        self.shouldSay("Art: .gamer gamename | .gamer gamename username "
                       "| .gamer - gamename")
