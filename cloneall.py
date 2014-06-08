#!/usr/bin/python3
"""
cloneall.py

A small command-line tool to clone all of a given username's public GitHub
repositories into the working directory.

Username is optional as an argument as it can be set within the program.

Usage: 
    python cloneall.py [-a|--all] [username]

"""

# Import libraries
import json
import urllib.request
import sys
import subprocess
from pprint import pprint

def get_json(url):
    """Takes url as argument, returns json data."""
    try:
        data = urllib.request.urlopen(url).read().decode("utf-8")
    except urllib.error.HTTPError:
        print("Username not found.")
        quit()
    else:
        return json.loads(data)


def api_url(username):
    """Returns github api url for a given username."""
    return "https://api.github.com/users/{}/repos?per_page=100".format(username)


def parse_args():
    """
    Returns a dictionary in the format
    {username:<string>,
     all:<boolean>}
    The key 'all' refers to whether all repos should automatically be cloned.
    """

    args = sys.argv[1:]  # Don't include filename.
    return_dict = {'username':"", 'all':False}  # Default values.
    if not args:
        return return_dict  # No input, get it from program.

    else:
        if "--all" in args or "-a" in args:
            # Set boolean, then remove all instances of "--all" or "-a" from list.
            return_dict['all'] = True
            args = [arg for element in args if element not in ["-a", "--all"]]
        
        # The element after "-u" or "--username" should be the username.
        if "--username" in args:
            return_dict['username'] = args[args.index("--username") + 1]
        elif "-u" in args:
            return_dict['username'] = args[args.index("-u") + 1]

        return return_dict

def print_repo_info(repo):
    """Pretty-prints information about repository."""
    print("\n -- {} -- \n".format(repo['name']))
    print("Description:\n{}\n".format(repo['description']))


def get_all():
    """Provides a prompt to query whether all items should be downloaded."""
    while True:
        get_all = input("Download all? [Y/N] ")
        if get_all in ['Y', 'y']:
            return True
        elif get_all in ['N', 'n']:
            return False

def get_username():
    """Provides a prompt to query the username to download from."""
    while True:
        username = input("Username: ")
        if username:
            return username


def clone_repo(repository):
    """Clones the repository passed to it using the git shell interface."""
    subprocess.call(["git", "clone", repository['git_url']])


def download_repos(repos, arguments):
    """Downloads repositories according to given arguments."""
    if repos:  # If list of repositories is not blank.
        for repo in repos:
            try:
                if arguments['all']:
                    # Skip printing repo info for each one.
                    clone_repo(repo)
                else:
                    print_repo_info(repo)  # Display name and description.
                    while True:
                        yesno = input("Clone repository? [Y/A/N/Q] ")
                        if yesno.lower() == 'y':
                            clone_repo(repo)
                            break

                        elif yesno.lower() == 'n':
                            print("Repository skipped.")
                            break

                        elif yesno.lower() == 'a':
                            clone_repo(repo)
                            arguments['all'] = True
                            break

                        elif yesno.lower() == 'q':
                            print("Exiting.")
                            return

            except subprocess.CalledProcessError:
                pass  # Error message shown anyway.
    else:
        print("User has no publicly available repositories.")


def main():
    arguments = parse_args()
    # Get info if it hasn't been specified in parameters.
    if not arguments['username']:
        arguments['username'] = get_username()


    # Get info from fetched JSON data.
    my_api_url = api_url(arguments['username'])
    json_data = get_json(my_api_url)

    if not arguments['all']:
        arguments['all'] = get_all()

    # Make a shorter, more manageable list of dictionaries:
    # (also makes sure github url is using HTTPS connection)
    repos = [{'name': repo['name'],
              'git_url': "https://" + repo['git_url'][6:],
              'description': repo['description']} for repo in json_data]
    download_repos(repos, arguments)


if __name__ == "__main__":
    main()
