import os
import shutil
import random
import string
import unittest
import subprocess
from gitautosync import pull_from_remote


class TestPullFromRemote(unittest.TestCase):

    init_path = './summer'
    repo_url = 'https://github.com/data-8/summer'

    def setUp(self):
        if os.path.exists(self.init_path):
            shutil.rmtree(self.init_path)

        subprocess.run(['gitautosync'])

    def test_repo_is_dirty(self):
        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertFalse(result)

        new_file_name = "{}/index.html".format(self.init_path)
        with open(new_file_name, 'w') as file:
            file.write(self.generate_random_string(10))

        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertTrue(result)

    def generate_random_string(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
