import json
import urllib.request
import sys
import subprocess
from pprint import pprint

def get_json(url):
    data = urllib.request.urlopen(url).read().decode("utf-8")
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

if __name__ == "__main__":
    arguments = parse_args(sys.argv)
    if not arguments['username']:
        arguments['username'] = input("Username: ")
    my_api_url = api_url(arguments['username'])
    json_data = get_json(my_api_url)
    repos = [{'name': repo['name'], 'git_url': "https://" + repo['git_url'][6:],
              'description': repo['description']} for repo in json_data]
    for repo in repos:
        if arguments['all']:
            subprocess.check_call(["git", "clone", repo['git_url']])
        else:
            print_repo_info(repo)
            while True:
                yesno = input("Clone repository? [Y/N]")
                if yesno.lower() == 'y':
                    subprocess.check_call(["git", "clone", repo['git_url']])
                    break
                elif yesno.lower() == 'n':
                    print("Repository skipped.")
                    break