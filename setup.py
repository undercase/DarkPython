from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
	name="DarkPython",
	version="1.0",
	description="",
	long_description="""
	""",
	author="",
	packages=find_packages(exclude='tests'),
	package_data={'darkpython': ['assets/*.png']},
	install_requires=['wxPython>=3.0'],
)
