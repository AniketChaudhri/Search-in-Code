# Base class for a repo

import os
from src.repo.github import GitHubRepo
from src.repo.local import LocalRepo


class RepoFactory:
    def __init__(self, link):
        self.link = link

    def make(self):
        if self.link.startswith("https://github.com"):
            return GitHubRepo(self.link)
        elif os.path.isdir(self.link):
            return LocalRepo(self.link)
        else:
            return None