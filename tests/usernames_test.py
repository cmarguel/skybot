import plugin_test
import plugins.usernames
from plugin_test import *


class UsernamesTest(plugin_test.PluginTest):

    def setUp(self):
        plugin_test.PluginTest.setUp(self, plugins.usernames)

    def test_no_data(self):
        nick('A').says('.usernames steam')
        self.shouldBeSilent()

    def test_add_username(self):
        nick('Art').says('.username steam')
        self.shouldSay("Art: Your username for steam isn't registered")

        nick('Art').says('.username steam art')
        self.shouldSay('Art: Noted: You use steam as "art"')

        nick('Art').says('.username steam')
        self.shouldSay('Art: Your steam username is "art"')
