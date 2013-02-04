# This is the test file for the Subtex package
import unittest
import sublime_plugin


# Running the tests
class subtex_testCommand(sublime_plugin.WindowCommand):
    def run(self, file_name="file_name"):
        # unittest.main(module=__name__, argv=[file_name], exit=False)
        self.window.run_command("make_pdf", {
        "cmd": ["latexmk", "-cd",
                "-e", "\"\\$pdflatex = 'pdflatex -shell-escape %O -interaction=nonstopmode -synctex=1 %S'\"",
                "-f", "-pdf"],
        "path": "$PATH:/usr/texbin:/usr/local/bin",
        "file_regex": "^(...*?):([0-9]+): ([0-9]*)([^\\.]+)",
        "file": "/Users/jakub/Documents/Thesis/Chapters/final.tex",
        "debug": True
        })