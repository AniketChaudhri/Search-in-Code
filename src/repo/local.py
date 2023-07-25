import os
from distutils.dir_util import copy_tree
import random
import unittest

from loguru import logger

from src import utils



class LocalRepo:
    # this gets a local directory as link, need to make a copy of it into this project gitrepos
    def __init__(self, link):
        self.link = link
        self.current_dir = os.getcwd()
        self.repo_path = os.path.join(self.current_dir, "src", "repo", "gitrepos")
        self.project_path = self.__copy(self.link)
        # self.__git_init(self.project_path)

    def clone_repo(self, link):
        '''Clone a repo from a link'''
        return self.__copy(link)

    def __check_if_git_repo(self):
        '''Check if git initialised in repo'''
        return True

    def __copy(self, link):
        # make a copy of given project directory
        project_folder_name = utils.get_hash(link)
        project_path = os.path.join(self.repo_path, str(project_folder_name))
        copy_tree(link, project_path)
        #TODO: Fix creation of 2 repos
        logger.info(project_path)
        return project_path

    def __git_init(self, project_path):
        # git init in the project directory
        os.chdir(project_path)
        os.system("git init")
        os.chdir(self.current_dir)

if __name__ == "__main__":
    class TestLocalRepo(unittest.TestCase):
        def test_local_repo(self):
            class args:
                path_to_repo= r'C:\Users\S9053161\Documents\projects\Search-in-Code\src\gitrepos\78218'
                model_name_or_path= 'krlvi/sentence-msmarco-bert-base-dot-v5-nlpl-code_search_net'
                query_text= 'print hello world'
            repo = LocalRepo(args.path_to_repo)
            print(repo.clone_repo(args.path_to_repo))

    RUN_ALL = False
    if RUN_ALL:
        unittest.main()
    else:
        suite = unittest.TestSuite()
        suite.addTest(TestLocalRepo('test_local_repo'))
        runner = unittest.TextTestRunner()
        runner.run(suite)


