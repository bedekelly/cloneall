"""
cloneall.py

A small command-line tool to clone all of a given username's public GitHub
repositories into the working directory.

Username is optional as an argument as it can be set within the program.

Usage: 
    python cloneall.py [-a|--all] [username]

"""
import json
import urllib.request
import sys
import subprocess
from pprint import pprint

def get_json(url):
    try:
        data = urllib.request.urlopen(url).read().decode("utf-8")
    except urllib.error.HTTPError:
        print("Username not found.")
        quit()
    else:
        return json.loads(data)


def get_username():
    while 1:
        username = input("Enter your username, or the username of the person whose"
                 " repositories you want to clone.")
        if username:
            break
        else:
            print("Please enter a valid username.")
    return username


def api_url(username):
    return "https://api.github.com/users/{}/repos".format(username)


def parse_args(sys_argv):
    """
    Returns a dictionary in the format
    {username:<string>,
     all:<boolean>}
    The key 'all' refers to whether all repos should automatically be cloned.
    """
    args = sys_argv[1:]
    args_dict = {}
    for arg in args:
        if arg in ["-a", "--all"]:
            args_dict['all'] = True
            break
    else:
        args_dict['all'] = False
    args = [arg for arg in args if arg not in ["-a", "--all"]]
    if len(args) > 0:
        args_dict['username'] = args[0]
    else:
        args_dict['username'] = None
    return args_dict


def print_repo_info(repo):
    print("\n -- {} -- \n".format(repo['name']))
    print("Description:\n{}\n".format(repo['description']))

def main():
    arguments = parse_args(sys.argv)
    if not arguments['username']:
        arguments['username'] = input("Username: ")
    my_api_url = api_url(arguments['username'])
    json_data = get_json(my_api_url)
    # Make a shorter, more manageable list:
    repos = [{'name': repo['name'], 'git_url': "https://" + repo['git_url'][6:],
              'description': repo['description']} for repo in json_data]
    if len(repos) >= 1:
        for repo in repos:
            if arguments['all']:
                # Skip printing repo info
                subprocess.check_call(["git", "clone", repo['git_url']])
            else:
                print_repo_info(repo)
                while True:
                    yesno = input("Clone repository? [Y/N/Q] ")
                    if yesno.lower() == 'y':
                        subprocess.check_call(["git", "clone", repo['git_url']])
                        break
                    elif yesno.lower() == 'n':
                        print("Repository skipped.")
                        break
                    elif yesno.lower() == 'q':
                        print("Exiting.")
                        quit()
    else:
        print("User has no publicly available repositories.")


if __name__ == "__main__":
    main()
else:
    print("This utility cannot be imported.")
