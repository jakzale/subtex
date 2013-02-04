import sublime, sublime_plugin
import os
import threading
import subprocess
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
    def run(self, cmd="", file_regex="", path="", file=None, debug=False):
        """Run command

        The following attributes are passed by the build system
            * cmd - the latex command
            * path - the additional path file
            * regex - the regex to capture the output
        """
        # Handling process killing
        if self.proc:
            self.output("\n\n### Got request to terminate compilation ###")
            self.proc.kill()
            self.proc = None
            return

        view = self.window.active_view()
        
        # Save if there are unchanged edits
        if view.is_dirty():
            print("Saving...")
            view.run_command('save')

        # Getting the proper file name
        # Using file switch for testing only
        if file:
            file_name = file
        else:
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
        # A bit crazy
        t_kwargs = {
            "file_name": file_name,
            "cmd": cmd + ["-outdir={}".format(tex_dir)],
            "path": path,
            "debug": debug
        }

        # Need to change dir here
        threading.Thread(target=self.thread, kwargs=t_kwargs).start()

    # This is the thread code
    def thread(self, file_name=None, cmd=None, path=None, debug=False):
        if not file_name and not cmd:
            self.output("Error, wrong invocation")
            return

        if self.proc:
            self.output("The proc handler is busy")
            return

        self.output("[Compiling {0}]".format(file_name))

        # This is ugly and risky as eel, but need to stick to it
        proc = None
        try:
            old_path = os.environ["PATH"]
            if path:
                os.environ["PATH"] = os.path.expandvars(path)
            t_cmd = cmd + [file_name]

            if debug:
                self.output("[DEBUG] Changed PATH From {} to {}".format(old_path, os.environ["PATH"]))
                self.output("[DEBUG] Executing command {}".format(t_cmd))
            
            proc = subprocess.Popen(t_cmd)

        except Exception as e:
            self.output("\n\nCOULD NOT COMPILE!\n\n")
            self.output("Attempted command:")
            self.output(" ".join(t_cmd))
            proc = None
            print(e)

        # Ensuring that the path is recovered
        finally:
            if path:
                os.environ["PATH"] = old_path
                if debug:
                    self.output("[DEBUG] Restored path to {}".format(os.environ["PATH"]))

        # We can gracefully return here if it did not succeed
        if not proc:
            return





    def output(self, string):
        self.output_view.run_command("output_print", {"text":string + "\n"})

class output_printCommand(sublime_plugin.TextCommand):
    """A simple class to print inside output panel"""
    def run(self, panel_edit, **args):
        panel = self.view
        if "text" in args:
            panel.insert(panel_edit, panel.size(), args["text"])
            panel.show(panel.size())
        else:
            print("[output_print]: Missing keyword text")


