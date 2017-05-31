import os
import random
import string
import unittest
import shutil
import git
from gitautosync import pull_from_remote


class TestPullFromRemote(unittest.TestCase):

    config = {
        "COPY_PATH": "",
        "ALLOWED_WEB_DOMAINS": "github.com",
        "GITHUB_DOMAIN": "github.com",
        "ALLOWED_GITHUB_ACCOUNTS": "data-8",
        "GITHUB_API_TOKEN": "",
        "MOCK_AUTH": True,
        "AUTO_PULL_LIST_FILE_NAME": ".autopull_list"
    }
    init_path = './summer'
    repo_url = 'https://github.com/data-8/summer'

    def setUp(self):
        pass

    def test_initialize_config(self):
        result = pull_from_remote._initialize_config('/.gitautosync/config.json')
        self.assertIsNotNone(result)
        self.assertTrue(result)
        self.assertIsInstance(result, dict)

    def test_initialize(self):
        if os.path.exists(self.init_path):
            shutil.rmtree(self.init_path)
        result = pull_from_remote._initialize_repo(
            self.repo_url,
            self.init_path,
            'gh-pages')

        self.assertIsNotNone(result)
        self.assertTrue(result)
        self.assertIsInstance(result, git.Repo)

    def test_make_commit_if_dirty(self):
        repo = git.Repo(self.init_path)
        result = pull_from_remote._make_commit_if_dirty(repo)
        self.assertIsNone(result)

        new_file_name = "{}/index.html".format(self.init_path)
        with open(new_file_name, 'w') as file:
            file.write(self.generate_random_string(10))

        result = pull_from_remote._make_commit_if_dirty(repo)

        self.assertIsNotNone(result)
        self.assertTrue(result)
        self.assertEquals(repo.head.commit.message.strip(), 'WIP')

    def test_pull_and_resolve_conflicts(self):
        repo = git.Repo(self.init_path)

        new_file_name = "{}/new_file_name.txt".format(self.init_path)
        with open(new_file_name, 'w') as file:
            file.write(self.generate_random_string(10))
        result = pull_from_remote._pull_and_resolve_conflicts(repo)

        self.assertIsNotNone(result)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(new_file_name))

    def generate_random_string(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
