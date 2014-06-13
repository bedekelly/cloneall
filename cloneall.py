#!/usr/bin/python3
"""
cloneall.py

A small command-line tool to clone all of a given username's public GitHub
repositories into the working directory.

Username is optional as an argument as it can be set within the program.

Usage: 
    python cloneall.py [-a|--all] [username]

"""
try:
    # Import libraries
    import json
    import urllib.request
    import sys
    import os
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
        # Pass PHP argument per_page with value 100; get 100 results per page.


    def parse_args():
        """
        Returns a dictionary in the format
        {username:<string>,
         dl_all:<boolean>,  # should download all repos
         ud_all:<boolean>}  # should update all existing repos
        """
        args = sys.argv[1:]  # Don't include filename.

        # By default the user has to pick whether to download/update all.
        return_dict = {'username': "",
                       'dl_all': False,
                       'ud_all': False,
                       'no_dl': False}

        if not args:
            return return_dict  # No input, get it from program.

        else:
            try:
                if "--download-all" in args or "-a" in args:
                    # Set boolean, then remove all instances of "--all" or "-a"
                    return_dict['dl_all'] = True
                    args = [arg for arg in args 
                        if arg not in ["-a", "--download-all"]]

                # "Download all" takes precedence over "No download".
                elif "--no-download" in args:
                    return_dict['no_dl'] = True
                    args = [arg for arg in args if arg != "--no-download"]

                if "--update-all" in args or "-p" in args:
                    # Same as above, for update rather than download.
                    return_dict['ud_all'] = True
                    args = [arg for arg in args
                        if arg not in ["-p", "--update-all"]]


                # The element after "-u" or "--username" should be the username.
                if "--username" in args:
                    return_dict['username'] = args[args.index("--username") + 1]
                elif "-u" in args:
                    return_dict['username'] = args[args.index("-u") + 1]
            except IndexError:
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
            get_all = input("Download all? [Y/N] ")
            if get_all in ['Y', 'y']:
                return True
            elif get_all in ['N', 'n']:
                return False


    def should_update_all():
        """Provides a prompt to query whether all items should be updated."""
        while True:
            get_all = input("Update all? [Y/N] ")
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


    def clone_repo(repository, arguments):
        """Clones the repository passed to it using the git program."""
        devnull = open(os.devnull, "w")
        try:
            subprocess.check_call(["git", "clone", repository['git_url']],
                                    stderr=devnull)
        except subprocess.CalledProcessError:
            # Error thrown when repo exists locally.
            if arguments['ud_all']:
                update_repository(repository['name'])
            elif should_update_repository(repository['name']):
                update_repository(repository['name'])
        else:
            print("Cloned {} successfully.".format(repository['name']))


    def should_update_repository(repo_name):
        """Provides a prompt to ask the user to update an existing repository."""
        while True:
            choice = input("Repository {} already exists here, update? [Y/N] "
                            .format(repo_name))
            if choice.lower() in ["y", "n"]:
                break
        return choice.lower() == 'y'


    def update_repository(repo_name):
        """Updates a given repository."""
        print("\nUpdating {}.".format(repo_name))
        try:
            os.chdir(repo_name)
        except:
            print("Something's gone wrong, will ignore repository.")
        else:
            try:
                output = subprocess.check_output(["git", "pull"])
                # Output is a byte string, need to decode.
                print(output.decode(sys.stdout.encoding))
            except subprocess.CalledProcessError:
                print("Something went badly wrong.")
            os.chdir("..")


    def download_repos(repos, arguments):
        """Downloads repositories according to given arguments."""
        if repos:  # If list of repositories is not blank.
            for repo in repos:
                try:
                    if arguments['dl_all']:
                        # Skip printing repo info for each one.
                        clone_repo(repo, arguments)
                    elif arguments['ud_all'] and os.path.exists(repo['name']):
                        update_repository(repo['name'])
                    elif not arguments['no_dl']:
                        print_repo_info(repo)  # Display name and description.
                        while True:
                            yesno = input("Clone repository? [Y/A/N/Q] ")
                            if yesno.lower() == 'y':
                                clone_repo(repo, arguments)
                                break

                            elif yesno.lower() == 'n':
                                print("Repository skipped.")
                                break

                            elif yesno.lower() == 'a':
                                clone_repo(repo, arguments)
                                arguments['dl_all'] = True
                                break

                            elif yesno.lower() == 'q':
                                print("Exiting.")
                                return

                except subprocess.CalledProcessError:
                    pass  # Error message printed anyway.
        else:
            print("User has no publicly available repositories.")


    def format_url(url):
        """Ensures URL is using HTTPS protocol."""
        return "https://" + url[6:]


    def main():
        """The main function for this program. Requests any input necessary, then
        carries out the instructions."""
        # Collect command-line switches.
        arguments = parse_args()

        # Get info if it hasn't been specified in parameters.
        if not arguments['username']:
            arguments['username'] = get_username()

        # Get info from fetched JSON data.
        my_api_url = api_url(arguments['username'])
        json_data = get_json(my_api_url)

        if not (arguments['dl_all'] or arguments['no_dl']):
            arguments['dl_all'] = should_download_all()

        if not arguments['ud_all']:
            arguments['ud_all'] = should_update_all()

        # Make a shorter, more manageable list of dictionaries:
        repos = [
                {'name': repo['name'],
                'git_url': format_url(repo['git_url']),
                'description': repo['description']}
                for repo in json_data
                ]

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
        try:
            import curses
        except ImportError:
            pass
        else:
            # _menu suffix denotes a Curses menu alternative.
            # Will implement soon.
            ...
            # main = main_menu
            # should_update_repository = should_ud_repo_menu
            # should_update_all = should_ud_all_menu
            # should_download_all = should_dl_all_menu
        main()
except (KeyboardInterrupt, EOFError):
    print("\nWill exit now.")