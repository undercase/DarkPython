from distutils.core import setup
import os
import py2exe

setup(
	name="DarkPython",
	version="1.0",
	description="A education-centered python IDE with a custom debugger.",
	author="Thomas Hobohm",
	author_email="superman3275@gmail.com",
	maintainer="Thomas Hobohm",
	data_files = ["assets/DarkPython.png", "assets/debug.png", "assets/interpret.png", "assets/newfile.png", "assets/open.png", "assets/save.png"],
	options = {'py2exe': {'optimize': 2, 'bundle_files': 2, "dll_excludes": ["MSVCP90.dll"], 'compressed': True}},
	windows = [{"script": "darkpython/darkpython.py"}, {"script": "darkpython/STCEdit.py"}, {"script": "darkpython/debugger.py"}, {"script": "darkpython/filenotebook.py"}],
	license="GNU GPL v3"
	)
