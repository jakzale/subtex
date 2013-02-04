import sublime
import os.path, re

# Parse magic comments to retrieve TEX root
# Stops searching for magic comments at first non-comment line of file
# Returns root file or current file

# Contributed by Sam Finn

def get_tex_root(view):
    try:
        root = os.path.abspath(view.settings().get('TEXroot'))
        if os.path.isfile(root):
            print("Main file defined in project settings : " + root)
            return root
    except:
        pass
    
    texFile = view.file_name()

    with open(texFile, 'r', encoding="utf-8") as f:
        line = f.readline()

        if not line.startswith('%'):
            root = texFile

        else:
            mroot = re.match(r"%\s*!TEX\s+root *= *(.*(tex|TEX))\s*$",line)
            if mroot:
                # we have a TEX root match 
                # Break the match into path, file and extension
                # Create TEX root file name
                # If there is a TEX root path, use it
                # If the path is not absolute and a src path exists, pre-pend it

                # Review this part of the code
                (texPath, texName) = os.path.split(texFile)
                (rootPath, rootName) = os.path.split(mroot.group(1))
                root = os.path.join(texPath,rootPath,rootName)
                root = os.path.normpath(root)

    return root