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
