Clone Them All
==============

Clones all of a user's repositories.

###Usage:
	python cloneall.py [-a|--all] [username]

If the -a or --all flag is not set, the script will ask about each repository in turn.

If the username is not given, the program will ask for it to be entered.

Example Usage:
	http://asciinema.org/a/9295

###Wishlist:

* Add "update repository" feature  ✓
* Add "update all" option
* Support more than 100 repositories per user
* Add ncurses front-end
* Add checks for git, python version etc.
* Persistence (only make these checks once)