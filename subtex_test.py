# This is the test file for the Subtex package
import unittest
import sublime_plugin

class TestSimple(unittest.TestCase):
    def test_fail(self):
        self.assertTrue(True)


# Running the tests
class subtex_testCommand(sublime_plugin.WindowCommand):
    def run(self, file_name="file_name"):
        unittest.main(module=__name__, argv=[file_name], exit=False)