import sublime, sublime_plugin

# This is my own sublime text latex plugin
# I am not sure if it will work properly,
# Still, I need at least some kind of build script

class ExampleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("Running")
        self.view.insert(edit, 0, "Hello, World!")
