import os
import shutil
import subprocess
import random
import string
import unittest
from gitautosync import pull_from_remote


class TestPullFromRemote(unittest.TestCase):

    init_path = 'summer'
    repo_url = 'https://github.com/data-8/summer'
    branch_name = 'gh-pages'

    def setUp(self):
        if os.path.exists(self.init_path):
            shutil.rmtree(self.init_path)
        pull_from_remote._initialize_repo(self.repo_url, self.init_path)

    def test_initialize_repo(self):
        self.assertTrue(os.path.exists(self.init_path))
        self.assertTrue(os.path.exists(self.init_path + "/.git"))

    def test_get_sub_cwd(self):
        result = pull_from_remote._get_sub_cwd(self.init_path)
        print("Repo Path w/ CWD:", result)
        self.assertTrue(os.path.exists(result) or not os.path.exists(self.init_path))

    def test_repo_is_dirty(self):
        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertFalse(result)

        self.make_repo_dirty()

        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertTrue(result)

    def test_make_commit(self):
        self.make_repo_dirty()
        pull_from_remote._make_commit(self.init_path, self.branch_name)
        cwd = pull_from_remote._get_sub_cwd(self.init_path)
        ps = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE, cwd=cwd)
        output = subprocess.check_output(['head', '-n', '1'], stdin=ps.stdout, cwd=cwd)
        ps.wait()
        output = output.decode('utf-8').strip().split(' ')[1]
        self.assertEqual(output, 'WIP')

        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertFalse(result)

    def test_pull_and_resolve_conflicts(self):
        cwd = pull_from_remote._get_sub_cwd(self.init_path)

        with open(self.init_path + "/new_file1.txt", 'w') as new_file:
            new_file.write(self.generate_random_string(10))

        pull_from_remote._make_commit(self.init_path, self.branch_name)

        with open(self.init_path + "/new_file2.txt", 'w') as new_file:
            new_file.write(self.generate_random_string(10))

        pull_from_remote._pull_and_resolve_conflicts(self.repo_url, self.init_path, self.branch_name)

        self.assertTrue(os.path.exists(self.init_path + "/new_file2.txt"))
        self.assertTrue(os.path.exists(self.init_path + "/new_file1.txt"))

        result = subprocess.check_output(['git', 'status'], cwd=cwd).decode('utf-8')
        self.assertIn('ahead', result)

    def make_repo_dirty(self):
        new_file_name = "{}/index.html".format(self.init_path)
        with open(new_file_name, 'w') as file:
            file.write(self.generate_random_string(10))

    def test_update_repo(self):
        self.make_repo_dirty()
        pull_from_remote._update_repo(self.repo_url, self.init_path, self.branch_name)
        cwd = pull_from_remote._get_sub_cwd(self.init_path)
        ps = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE, cwd=cwd)
        output = subprocess.check_output(['head', '-n', '1'], stdin=ps.stdout, cwd=cwd)
        ps.wait()
        output = output.decode('utf-8').strip().split(' ')[1]
        self.assertEqual(output, 'WIP')

        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertFalse(result)

        with open(self.init_path + "/new_file1.txt", 'w') as new_file:
            new_file.write(self.generate_random_string(10))

        pull_from_remote._make_commit(self.init_path, self.branch_name)

        with open(self.init_path + "/new_file2.txt", 'w') as new_file:
            new_file.write(self.generate_random_string(10))

        pull_from_remote._pull_and_resolve_conflicts(self.repo_url, self.init_path, self.branch_name)

        self.assertTrue(os.path.exists(self.init_path + "/new_file2.txt"))
        self.assertTrue(os.path.exists(self.init_path + "/new_file1.txt"))

        result = subprocess.check_output(['git', 'status'], cwd=cwd).decode('utf-8')
        self.assertIn('ahead', result)

    def test_pull_from_remote(self):
        if os.path.exists(self.init_path):
            shutil.rmtree(self.init_path)
        pull_from_remote.pull_from_remote(self.repo_url, self.branch_name, self.init_path)
        self.assertTrue(os.path.exists(self.init_path))
        self.assertTrue(os.path.exists(self.init_path + "/.git"))

        self.make_repo_dirty()

        pull_from_remote.pull_from_remote(self.repo_url, self.branch_name, self.init_path)
        cwd = pull_from_remote._get_sub_cwd(self.init_path)
        ps = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE, cwd=cwd)
        output = subprocess.check_output(['head', '-n', '1'], stdin=ps.stdout, cwd=cwd)
        ps.wait()
        output = output.decode('utf-8').strip().split(' ')[1]
        self.assertEqual(output, 'WIP')

        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertFalse(result)

        with open(self.init_path + "/new_file1.txt", 'w') as new_file:
            new_file.write(self.generate_random_string(10))

        pull_from_remote._make_commit(self.init_path, self.branch_name)

        with open(self.init_path + "/new_file2.txt", 'w') as new_file:
            new_file.write(self.generate_random_string(10))

        pull_from_remote._pull_and_resolve_conflicts(self.repo_url, self.init_path, self.branch_name)

        self.assertTrue(os.path.exists(self.init_path + "/new_file2.txt"))
        self.assertTrue(os.path.exists(self.init_path + "/new_file1.txt"))

        result = subprocess.check_output(['git', 'status'], cwd=cwd).decode('utf-8')
        self.assertIn('ahead', result)

    def generate_random_string(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
