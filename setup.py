#!/usr/bin/python3
from distutils.core import setup
setup(name='cloneall',
	  version='1.0.4',
	  description="Clone GitHub repositories",
	  author="Bede Kelly",
	  author_email="bedekelly97@gmail.com",
	  url="https://github.com/bedekelly/clone-them-all",
	  requires=['SimpleMenu'],
	  # dependency_links=['https://pypi.python.org/packages/source/S/SimpleMenu/SimpleMenu-1.0.tar.gz'],
	  scripts=['cloneall'])
