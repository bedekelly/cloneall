#!/usr/bin/env python3.4
"""
cloneall
Clones all of a user's repositories.

Usage:
    cloneall OPTIONS...

Options:
    cloneall -u <username>
    cloneall --no-download // --download-all
    cloneall --no-update // --update-all
"""

import json
import readline
import urllib.request
import sys
import os
import subprocess
from pprint import pprint


def get_json(url):
    """Takes url as argument, returns json data from GitHub."""
    try:
        # Open a file handle to the data, then load it as JSON
        data = urllib.request.urlopen(url).read().decode("utf-8")
        json_ = json.loads(data)
    except urllib.error.HTTPError:
        # Github API returns a 404 HTTP error.
        print("Username not found.")
        quit()
    except urllib.error.URLError:
        # Can't resolve Github through DNS.
        print("Host unknown. Please check your internet connection.")
        quit()
    except ValueError:
        # No HTTP error, but incorrect webpage coming through - happens when page is redirected.
        print("Connection error - please check your internet connnection is working."
              "This error is often encountered when unauthenticated using a proxy or captive portal.")
        quit()
    else:
        return json_
        
        
def parse_args():
    """
    Sifts through the command-line arguments given.
    Returns a dictionary in the format:
    {username:<string>,
    dl_all:<boolean>,  # Should download all user's repos
    ud_all:<boolean>,  # Should update all existing repos
    no_dl:<boolean>}   # Only update existing repos
    """
    args = sys.argv[1:]  # Don't include filename.
    
    # By default the user has to pick whether to download/update all.
    return_dict = {'username': "",
                   'dl_all': False,
                   'ud_all': False,
                   'no_dl': False}
    
    if not args:
        return return_dict  # No input given, so we explicitly request it.
        
    else:
        try:
            if "--download-all" in args or "-a" in args:
                # Test for Download-All flags, then remove from our input.
                return_dict['dl_all'] = True
                args = [arg for arg in args
                        if arg not in ["-a", "--download-all"]]

            elif "--no-download" in args:
                # Test for No-Download flags, then remove from our input.
                return_dict['no_dl'] = True
                args = [arg for arg in args if arg != "--no-download"]
                
            if "--update-all" in args or "-p" in args:
                # Test for Update-All flags, then remove from our input.
                return_dict['ud_all'] = True
                args = [arg for arg in args
                        if arg not in ["-p", "--update-all"]]
                    
                    
            # The element after "-u" or "--username" should be the username.
            if "--username" in args:
                return_dict['username'] = args[args.index("--username") + 1]
            elif "-u" in args:
                return_dict['username'] = args[args.index("-u") + 1]

        except IndexError:
            # User typed an option after -u, instead of a username.
            # This option was removed, so we get an IndexError trying to get the next item along.
            print(__doc__)
            quit()
        return return_dict

def print_repo_info(repo):
    """Pretty-prints information about repository."""
    print("\n -- {} -- \n".format(repo['name']))
    print("Description:\n{}\n".format(repo['description']))
    
    
def should_download_all():
    """Provides a prompt to query whether all items should be downloaded."""
    while True:
        # Loop until a valid input is acquired.
        get_all = input("Download all? [Y/N] ")
        if get_all in ['Y', 'y']:
            return True
        elif get_all in ['N', 'n']:
            return False


def _curses_should_download_all():
    """Curses menu for should_download_all."""
    # Create a menu, show it, and get the user's choice.
    newmenu = Menu("Yes", "No", title="Download all repositories?")
    choice = newmenu.show()
    if choice:
        return choice == "Yes"
    # Choice is None, so the user pressed Q.
    print("Exiting.")
    quit()


def should_update_all():
    """Provides a prompt to query whether all items should be updated."""
    while True:
        # Loop until a valid input is provided.
        get_all = input("Update all? [Y/N] ")
        if get_all in ['Y', 'y']:
            return True
        elif get_all in ['N', 'n']:
            return False


def _curses_should_update_all():
    """Curses menu for should_update_all. Will be patched over should_update_all if needed."""
    # Create a menu, show it, and get the user's choice.
    newmenu = Menu("Yes", "No", title="Update all existing repositories?")
    choice = newmenu.show()
    if choice:
        return choice == "Yes"
    # Choice is None, user pressed Q.
    print("Exiting.")
    quit()


def get_username():
    """Provides a prompt to query the username to download from."""
    while True:
        # Loop until we get a valid input.
        username = input("Username: ")
        if username:  # is not the empty string:
            return username
        print("Please enter a valid username.")
        
def clone_repo(repository, arguments):
    """Clones the repository passed to it using the git program."""
    # Open a file handle so we can discard unnecessary program output.
    devnull = open(os.devnull, "w")
    try:
        command = ["git", "clone", repository['git_url']]
        # Try cloning; write all stdout to null and catch errors here.
        subprocess.check_call(command, stdout=devnull)
    except subprocess.CalledProcessError as e:
        # Error thrown when repo exists locally.
        # Has the user specified if we should update it automatically?
        if arguments['ud_all']:
            update_repository(repository['name'])
        # If not, ask them if they'd like to.
        elif should_update_repository(repository['name']):
            update_repository(repository['name'])
    else:
        print("Cloned {} successfully.".format(repository['name']))


def should_update_repository(repo_name):
    """Provides a prompt to ask the user to update an existing repository."""
    while True:
        # Loop until we get a valid input.
        choice = input("Repository {} already exists here, update? [Y/N] "
                       .format(repo_name))
        if choice.lower() in ["y", "n"]:
            break
            return choice.lower() == 'y'


def _curses_should_update_repository(repo_name):
    """Curses version of should_update_repository."""
    # Create a menu, show it, and get the user's choice.
    menu_title = "Repository {} already exists. Update?".format(repo_name)
    menu = Menu("Yes", "No", title=menu_title)
    choice = menu.show()
    if choice:
        return choice == "Yes"
        # Choice is None, user pressed Q.
        print("Exiting.")
        quit()


def should_download_repository(repo):
    """Provides a prompt to ask the user to download a repository."""
    print_repo_info(repo)  # Display name and description.
    while True:
        # Loop until we get valid input
        yesno = input("Clone repository? [Y/A/N/Q] ")
        if yesno.lower() in ["y", "n", "a"]:
            return yesno.lower()
        elif yesno.lower() == "q":
            quit()
            
            
def _curses_should_download_repository(repo):
    """Curses version of should_download_repo."""
    # Create a menu, show it, and get the user's choice.
    menu = Menu("Download",
                "Skip",
                "Download All",
                title=repo['name'],
                subtitle=repo['description'])
    choice = menu.show()
    # Convert our menu choice into a program-readable single character.
    choice_dict = {"Download": "y",
                   "Skip": "n",
                   "Download All": "a"}
    if choice:
        return choice_dict[choice]
    # Choice is None, user pressed Q.
    quit()


def update_repository(repo_name):
    """Updates a given repository."""
    print("\nUpdating {}.".format(repo_name))
    try:
        # Change into the repo's directory.
        os.chdir(repo_name)
    except Exception as e:
        print(e)
        print("Something's gone wrong, will ignore repository.")
    else:
        try:
            output = subprocess.check_output(["git", "pull"])
            # Output is a byte string, need to decode.
            print(output.decode(sys.stdout.encoding))
        except subprocess.CalledProcessError:
            # Shouldn't happen with working Git.
            print("Something went badly wrong. Please check your git install.")
    os.chdir("..")


def download_repos(repos, arguments):
    """Downloads repositories according to given arguments."""
    if repos:
        for repo in repos:
            if arguments['dl_all']:
                # Skip printing repo info for each one.
                clone_repo(repo, arguments)
                update_repository(repo['name'])
            elif arguments['ud_all'] and os.path.exists(repo['name']):
                update_repository(repo['name'])
            elif not arguments['no_dl']:
                choice = should_download_repository(repo)
                if choice == "y":
                    clone_repo(repo, arguments)
                elif choice == "a":
                    clone_repo(repo, arguments)
                    arguments['dl_all'] = True
                        
    else:  # List of repositories we have is blank.
        print("User has no publicly available repositories.")


def https(url):
    if url.startswith("http://"):
        return url[:4] + "s" + url[4:] 
    return url


def main():
    """The main function for this program. Requests any input necessary, then
    carries out the instructions."""
    # Collect command-line switches.
    arguments = parse_args()

    # Get info if it hasn't been specified in parameters.
    if not arguments['username']:
        arguments['username'] = get_username()
        
    api_url = "https://api.github.com/users/"\
              "{}/repos?per_page=100".format

    # Get info from fetched JSON data.
    my_api_url = api_url(arguments['username'])
    json_data = get_json(my_api_url)
    
    # If info not specified, request it now.
    if not (arguments['dl_all'] or arguments['no_dl']):
        arguments['dl_all'] = should_download_all()
    if not arguments['ud_all']:
        arguments['ud_all'] = should_update_all()

    # Make a shorter, more manageable list of dictionaries:
    repos = [{'name': repo['name'],
              'git_url': https(repo['git_url']),
              'description': repo['description']}
             for repo in json_data]

    download_repos(repos, arguments)


if __name__ == "__main__":
    # Check if Git is installed (vital).
    try:
        devnull = open(os.devnull, "w")
        subprocess.check_call(["git", "--version"], stdout=devnull)
    except subprocess.CalledProcessError:
        print("Git version control system required.")
        quit()

    # Check if Curses is installed (nonvital).
    if "--no-curses" not in sys.argv:
        try:
            import curses
            os.get_terminal_size
        except ImportError:
            pass
        except AttributeError:
            print("Fetching terminal size not supported, falling back to "
                      "standard input.")
        else:
            try:
                from SimpleMenu import Menu
                # Replace text menus with curses alternatives in the global namespace
                should_update_repository = _curses_should_update_repository
                should_download_repository = _curses_should_download_repository
                should_update_all = _curses_should_update_all
                should_download_all = _curses_should_download_all
            except ImportError:
                # SimpleMenu not present, can't have replaced any menus
                print("Menu support requires SimpleMenu.py, will fall"
                      " back to standard input.")
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # User presses C-c or C-d (respectively: kill process or EOF)
        print("\nWill exit now.")
        quit()
