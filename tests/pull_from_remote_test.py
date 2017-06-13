import os
import shutil
import subprocess
import random
import string
import unittest
from gitautosync import pull_from_remote


class TestPullFromRemote(unittest.TestCase):

    init_path = 'test-repo'
    repo_url = 'https://github.com/data-8/test-homework'
    branch_name = 'gh-pages'

    def setUp(self):
        self.delete_init_path()
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

        self.assertEqual(self.get_latest_commit_msg(), 'WIP')

        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertFalse(result)

    def test_pull_and_resolve_conflicts(self):
        self.retains_new_files()

        self.assertIn('ahead', self.get_git_status_msg())

    def test_update_repo(self):
        self.make_repo_dirty()
        pull_from_remote._update_repo(self.repo_url, self.init_path, self.branch_name)
        self.assertEqual(self.get_latest_commit_msg(), 'WIP')

        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertFalse(result)

        self.retains_new_files()

        self.assertIn('ahead', self.get_git_status_msg())

    def test_pull_from_remote(self):
        self.delete_init_path()
        pull_from_remote.pull_from_remote(self.repo_url, self.branch_name, self.init_path)

        self.assertTrue(os.path.exists(self.init_path))
        self.assertTrue(os.path.exists(self.init_path + "/.git"))

        self.make_repo_dirty()

        pull_from_remote.pull_from_remote(self.repo_url, self.branch_name, self.init_path)
        self.assertEqual(self.get_latest_commit_msg(), 'WIP')

        result = pull_from_remote._repo_is_dirty(self.init_path)
        self.assertFalse(result)

        self.retains_new_files()

        self.assertIn('ahead', self.get_git_status_msg())

    def test_pull_deleted_files(self):
        deleted_file_name = '{}/README.md'.format(self.init_path)
        subprocess.check_call(['rm', deleted_file_name])
        pull_from_remote._reset_deleted_files(self.init_path, self.branch_name)
        self.assertTrue(os.path.exists(deleted_file_name))

    def generate_random_string(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

    def get_latest_commit_msg(self):
        cwd = pull_from_remote._get_sub_cwd(self.init_path)
        ps = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE, cwd=cwd)
        output = subprocess.check_output(['head', '-n', '1'], stdin=ps.stdout, cwd=cwd)
        ps.wait()
        return output.decode('utf-8').strip().split(' ')[1]

    def create_new_file(self, name):
        with open(self.init_path + "/" + name, 'w') as new_file:
            new_file.write(self.generate_random_string(10))

    def get_git_status_msg(self):
        cwd = pull_from_remote._get_sub_cwd(self.init_path)
        return subprocess.check_output(['git', 'status'], cwd=cwd).decode('utf-8')

    def make_repo_dirty(self):
        new_file_name = "{}/README.md".format(self.init_path)
        with open(new_file_name, 'w') as file:
            file.write(self.generate_random_string(10))

    def delete_init_path(self):
        if os.path.exists(self.init_path):
            shutil.rmtree(self.init_path)

    def retains_new_files(self):
        self.create_new_file("new_file1.txt")

        pull_from_remote._make_commit(self.init_path, self.branch_name)

        self.create_new_file("new_file2.txt")

        pull_from_remote._pull_and_resolve_conflicts(self.repo_url, self.init_path, self.branch_name)

        self.assertTrue(os.path.exists(self.init_path + "/new_file2.txt"))
        self.assertTrue(os.path.exists(self.init_path + "/new_file1.txt"))
