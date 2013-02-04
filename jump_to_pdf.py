import sublime, sublime_plugin, os.path, subprocess, time
from subtex.get_tex_root import get_tex_root 

# Jump to current line in PDF file
# NOTE: must be called with {"from_keybinding": <boolean>} as arg

class jump_to_pdfCommand(sublime_plugin.TextCommand):
    def run(self, edit, from_keybinding=False):
        # Check prefs for PDF focus and sync
        print("[subtex] jumping to pdf")
        s = sublime.load_settings("subtex.sublime-settings")
        prefs_keep_focus = s.get("keep_focus", True)
        keep_focus = self.view.settings().get("keep focus",prefs_keep_focus)
        prefs_forward_sync = s.get("forward_sync", True)
        forward_sync = self.view.settings().get("forward_sync",prefs_forward_sync)

        # If invoked from keybinding, we focus the PDF and sync
        # Rationale: if the user invokes the jump command, s/he wants to see the result of the compilation.
        # If the PDF viewer window is already visible, s/he probably wants to sync, or s/he would have no
        # need to invoke the command. And if it is not visible, the natural way to just bring up the
        # window without syncing is by using the system's window management shortcuts.
        
        if from_keybinding:
            keep_focus = False
            forward_sync = True

        print(from_keybinding, keep_focus, forward_sync)

        tex_file, tex_ext = os.path.splitext(self.view.file_name())
        if tex_ext.lower() != ".tex":
            sublime.error_message("{} is not a TeX source file: cannot jump.".format(os.path.basename(self.view.file_name())))
            return


        quotes = "\""
        srcfile = tex_file + '.tex'
        root = get_tex_root(self.view)

        print("[subtex] !TEX root =", repr(root)) # need something better here, but this works.
        rootName, rootExt = os.path.splitext(root)
        pdffile = rootName + '.pdf'
        
        (line, col) = self.view.rowcol(self.view.sel()[0].end())
        print("[subtex] jumping to:", line, col)
        
        # column is actually ignored up to 0.94
        # HACK? It seems we get better results incrementing line
        line += 1

        # Query view settings to see if we need to keep focus or let the PDF viewer grab it
        # By default, we respect settings in Preferences
        
        # Clear it up a bit
        options = ["-r","-g"] if keep_focus else ["-r"]
        print(options)
        if forward_sync:
            print(" ".join(["/Applications/Skim.app/Contents/SharedSupport/displayline"] + 
                            options + [str(line), pdffile, srcfile]))
            subprocess.Popen(["/Applications/Skim.app/Contents/SharedSupport/displayline"] + 
                            options + [str(line), pdffile, srcfile])
        else:
            skim = os.path.join(sublime.packages_path(),
                            'subtex', 'skim', 'displayfile')
            subprocess.Popen(['sh', skim] + options + [pdffile])

