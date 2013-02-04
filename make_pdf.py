import sublime, sublime_plugin
import os
import threading
import subprocess
from subtex.get_tex_root import get_tex_root
from subtex.parse_tex_log import parse_tex_log
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
            # Not sure if this is needed, but to avoid race conditions
            proc = self.proc
            self.proc = None
            proc.kill()
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
        _, tex_ext = os.path.splitext(file_name)
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
        print("[make_pdf] Number of active threads: {}".format(threading.active_count()))

    # This is the thread code
    def thread(self, file_name=None, cmd=None, path=None, debug=False):
        # Clearing the output panel
        self.output_view.run_command("output_clear")

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

            print(" ".join(t_cmd))            
            proc = subprocess.Popen(t_cmd)

        except Exception as e:
            self.output("\n\nCOULD NOT COMPILE!\n\n")
            self.output("Attempted command:")
            self.output(" ".join(t_cmd))
            proc = None
            print("[subtext_thread] Error: {}".format(e))

        # Ensuring that the path is recovered
        finally:
            if path:
                os.environ["PATH"] = old_path
                if debug:
                    self.output("[DEBUG] Restored path to {}".format(os.environ["PATH"]))

        # We can gracefully return here if it did not succeed
        if not proc:
            return

        # Setting up the handle for the proc
        self.proc = proc

        # Waiting for the proc to finish
        proc.wait()

        # Cheching if the compilation have been cancelled
        if not self.proc:
            # The process have been cancelled
            print("[subtex] Process Terminated by user.")
            print("         process returned {}".format(proc.returncode))
            self.output("\n[Compilation process terminated by user]")
            self.finish()
            return
        else:
            # Everything was done clearly, release the proc handle
            self.proc = None

        print("[subtex] Finished normally")
        print("         process returned {}".format(proc.returncode))

        # Processing the log
        
        tex_base, _ = os.path.splitext(file_name)
        data = None
        log_file = tex_base + ".log" 
        with open(log_file, 'rb') as f:
            data = f.read()

        if not data:
            print("[subtex] Error reading log file {}".format(log_file))
            return

        errors = []
        warnings = []

        try:
            (errors, warnings) = parse_tex_log(data)
            content = [""]
            if errors:
                content.append("There were errors in your LaTeX source") 
                content.append("")
                content.extend(errors)
            else:
                content.append("Texification succeeded: no errors!")
                content.append("") 
            if warnings:
                if errors:
                    content.append("")
                    content.append("There were also warnings.") 
                else:
                    content.append("However, there were warnings in your LaTeX source") 
                content.append("")
                content.extend(warnings)

        # Exception Handling
        except Exception as e:
            content=["",""]
            content.append("LaTeXtools could not parse the TeX log file")
            content.append("(actually, we never should have gotten here)")
            content.append("")
            content.append("Python exception: " + repr(e))
            content.append("")
            content.append("Please let me know on GitHub. Thanks!")

        self.output("\n".join(content))
        self.output("\n[Done!]")
        self.finish(len(errors) == 0)

    def output(self, string):
        self.output_view.run_command("output_print", {"text":string + "\n"})

    def finish(self, should_switch=False):
        self.output_view.run_command("output_rewind")
        if should_switch:
           self.window.active_view().run_command("jump_to_pdf") 

class output_printCommand(sublime_plugin.TextCommand):
    """A simple class to print inside output panel"""
    def run(self, panel_edit, text=None, position=False):
        panel = self.view
        if text:
            panel.insert(panel_edit, panel.size(), text)
            if position:
                panel.show(panel.size())
        else:
            print("[output_print]: Missing keyword text")

class output_rewindCommand(sublime_plugin.TextCommand):
    """Simple command to show the top of the output window"""
    def run(self, edit):
        panel = self.view
        panel.show(0)

class output_clearCommand(sublime_plugin.TextCommand):
    """Simple command to clear the view"""
    def run(self, edit):
        panel = self.view
        all = sublime.Region(0, panel.size())
        panel.erase(edit, all)


