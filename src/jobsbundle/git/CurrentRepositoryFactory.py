import os
from pygit2 import Repository, discover_repository, GitError # pylint: disable = no-name-in-module

class CurrentRepositoryFactory:

    def create(self):
        basePath = os.getcwd()
        repositoryPath = discover_repository(basePath)

        if not repositoryPath:
            raise GitError(f'No repository found at "{basePath}" and its parents')

        return Repository(repositoryPath)
