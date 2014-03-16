from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
	name="DarkPython",
	version="1.0",
	description="Pure-python IDE with custom debugger for use in the classroom.",
	long_description="""
	""",
	author="Thomas Hobohm (superman3275)",
	packages=find_packages(exclude='tests'),
	package_data={'darkpython': ['assets/*.png']},
	install_requires=['wxPython>=3.0'],
)
