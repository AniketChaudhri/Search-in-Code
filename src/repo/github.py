import os
import random
import re
import shutil
import subprocess
import validators
import requests

# Threshold for maximum folder size (in bytes). This is set to 100MB
MAX_SIZE = 100000000

class GitHubRepo:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.repo_path = os.path.join(self.current_dir, "src", "gitrepos")
        # print(self.current_dir)
        pass

    def _check_if_valid_url(self, url):
        validation = validators.url(url, public=True)

        if validation == True:
            pattern = "^https:\/\/github\.com\/[A-Za-z0-9-]+\/[A-Za-z0-9-_.]+$"
            match = re.match(pattern, url)

            if match:
                respnse = requests.get(url)
                if respnse.status_code == 200:
                    return True
            else:
                return False
        else:
            return False
        return False

    def _check_if_public(self, url):
        if self._check_if_valid_url(url=url):
            return "Yes"
        elif os.path.isdir(os.path.join("/mnt", url[1:])):
            return "No"
        else:
            return "Error"

    def _get_folder_size(self, folder):
        return 1
        total_size = 0
        for path, dirs, files in os.walk(folder):
            for f in files:
                fp = os.path.join(path, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    def clone_repo(self, url):
        # check if valid url
        if not self._check_if_valid_url(url=url):
            return False, ""
        project_folder_name = random.randint(10000, 99999)
        project_path = os.path.join(self.repo_path, str(project_folder_name))

        while os.path.isdir(project_path):
            project_folder_name = random.randint(10000, 99999)
            project_path = os.path.join(self.repo_path, str(project_folder_name))

        os.makedirs(project_path)
        git_process = subprocess.Popen(["git", "clone", url, project_path])

        # Periodically check folder size
        while git_process.poll() is None:
            folder_size = self._get_folder_size(project_path)
            # print(folder_size)
            if folder_size > MAX_SIZE:
                git_process.terminate()
                print("Error: Git clone process terminated, folder size exceeded threshold.")
                shutil.rmtree(project_path)
                return False, ""

        return True, project_path