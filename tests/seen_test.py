import plugin_test
import plugins.seen
from plugin_test import *


class SeenTest(plugin_test.PluginTest):

    def setUp(self):
        plugin_test.PluginTest.setUp(self)
        plugin_test.PluginTest.preparePlugins(self, plugins.seen)

    def test_seen_self(self):
        nick("Art").says("hello world")
        nick("Art").says(".seen Art")
        self.shouldSay("Art: Have you looked in a mirror lately?")

    def test_seen_other(self):
        nick("Art").says("hello world")
        nick("Bob").says(".seen Art")
        self.shouldSay(
            "Bob: art was last seen 0 minutes ago saying: hello world")

    def test_never_seen(self):
        nick("Bob").says(".seen Art")
        self.shouldSay("Bob: I've never seen art")

    def test_seen_after_some_time(self):
        nick("Art").says("hello world")

        after(10, "minutes")
        nick("Bob").says(".seen Art")
        self.shouldSay(
            "Bob: art was last seen 10 minutes ago saying: hello world")
