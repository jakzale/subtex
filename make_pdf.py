import sublime, sublime_plugin
import os.path
from subtex.get_tex_root import get_tex_root
# This is my own sublime text latex plugin
# I am not sure if it will work properly,
# Still, I need at least some kind of build script

class make_pdfCommand(sublime_plugin.WindowCommand):
    """Make PDF command that compiles the given latex file"""
    def __init__(self, window):
        super().__init__(window)
        # Instance variables go here
        self.proc = None
        self.output_view = None

    # Shouldn't it be easier
    def run(self, cmd="", file_regex="", path=""):
        """Run command

        The following attributes are passed by the build system
            * cmd - the latex command
            * path - the additional path file
            * regex - the regex to capture the output
        """
        view = self.window.active_view()
        
        # Save if there are unchanged edits
        if view.is_dirty():
            print("Saving...")
            view.run_command('save')

        # Getting the proper file name
        file_name = get_tex_root(view)
        if not os.path.isfile(file_name):
            sublime.error_message(file_name + ": file not found.")
            return

        # Check for the tex extension
        tex_base, tex_ext = os.path.splitext(file_name)
        tex_dir = os.path.dirname(file_name)
        
        if tex_ext.lower() != ".tex":
            sublime.error_message("%s is not a Tex source file: cannot compile" % os.path.basename(view.file_name()))
            return

        print(cmd, file_name)

        # Creating the output view
        if not self.output_view:
            self.output_view = self.window.get_output_panel("subtexexec")
        
        # Showing the output
        self.window.run_command("show_panel", {"panel": "output.subtexexec"})
        self.output("Hello, World!\n")

    def output(self, string):
        self.output_view.run_command("output_print", {"text":string})

class output_printCommand(sublime_plugin.TextCommand):
    """A simple class to print inside output panel"""
    def run(self, panel_edit, **args):
        panel = self.view
        if "text" in args:
            panel.insert(panel_edit, panel.size(), args["text"])
            panel.show(panel.size())
        else:
            print("[output_print]: Missing keyword text")

