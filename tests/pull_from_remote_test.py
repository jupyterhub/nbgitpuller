import os
import shutil
import subprocess
import random
import string
import unittest
from gitautosync.pull_from_remote import GitAutoSync


class TestPullFromRemote(unittest.TestCase):

    _gitautosync = None

    def setUp(self):
        self._gitautosync = GitAutoSync(
            'https://github.com/data-8/test-homework',
            'gh-pages',
            'test-repo'
        )
        self.delete_init_path()
        self._gitautosync._initialize_repo()

    def test_initialize_repo(self):
        self.assertTrue(os.path.exists(self._get_repo_dir()))
        self.assertTrue(os.path.exists(self._get_repo_dir() + "/.git"))

    def test_get_sub_cwd(self):
        result = self._gitautosync._get_sub_cwd()
        print("Repo Path w/ CWD:", result)
        self.assertTrue(os.path.exists(result) or not os.path.exists(self._get_repo_dir()))

    def test_repo_is_dirty(self):
        result = self._gitautosync._repo_is_dirty()
        self.assertFalse(result)

        self.make_repo_dirty()

        result = self._gitautosync._repo_is_dirty()
        self.assertTrue(result)

    def test_make_commit(self):
        self.make_repo_dirty()
        self._gitautosync._make_commit()

        self.assertEqual(self.get_latest_commit_msg(), 'WIP')

        result = self._gitautosync._repo_is_dirty()
        self.assertFalse(result)

    def test_pull_and_resolve_conflicts(self):
        self.retains_new_files()

        self.assertIn('ahead', self.get_git_status_msg())

    def test_update_repo(self):
        self.make_repo_dirty()
        self._gitautosync._update_repo()
        self.assertEqual(self.get_latest_commit_msg(), 'WIP')

        result = self._gitautosync._repo_is_dirty()
        self.assertFalse(result)

        self.retains_new_files()

        self.assertIn('ahead', self.get_git_status_msg())

    def test_pull_from_remote(self):
        self.delete_init_path()
        self._gitautosync.pull_from_remote()

        self.test_initialize_repo()

        self.make_repo_dirty()

        self._gitautosync.pull_from_remote()
        self.assertEqual(self.get_latest_commit_msg(), 'WIP')

        result = self._gitautosync._repo_is_dirty()
        self.assertFalse(result)

        self.retains_new_files()

        self.assertIn('ahead', self.get_git_status_msg())

    def test_pull_deleted_files(self):
        deleted_file_name = '{}/README.md'.format(self._get_repo_dir())
        subprocess.check_call(['rm', deleted_file_name])
        self._gitautosync._reset_deleted_files()
        self.assertTrue(os.path.exists(deleted_file_name))

    def generate_random_string(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

    def get_latest_commit_msg(self):
        cwd = self._gitautosync._get_sub_cwd()
        ps = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE, cwd=cwd)
        output = subprocess.check_output(['head', '-n', '1'], stdin=ps.stdout, cwd=cwd)
        ps.wait()
        return output.decode('utf-8').strip().split(' ')[1]

    def create_new_file(self, name):
        with open(self._get_repo_dir() + "/" + name, 'w') as new_file:
            new_file.write(self.generate_random_string(10))

    def get_git_status_msg(self):
        cwd = self._gitautosync._get_sub_cwd()
        return subprocess.check_output(['git', 'status'], cwd=cwd).decode('utf-8')

    def make_repo_dirty(self):
        new_file_name = "{}/README.md".format(self._get_repo_dir())
        with open(new_file_name, 'w') as file:
            file.write(self.generate_random_string(10))

    def delete_init_path(self):
        if os.path.exists(self._get_repo_dir()):
            shutil.rmtree(self._get_repo_dir())

    def retains_new_files(self):
        self.create_new_file("new_file1.txt")

        self._gitautosync._make_commit()

        self.create_new_file("new_file2.txt")

        self._gitautosync._pull_and_resolve_conflicts()

        self.assertTrue(os.path.exists(self._get_repo_dir() + "/new_file2.txt"))
        self.assertTrue(os.path.exists(self._get_repo_dir() + "/new_file1.txt"))

    def _get_repo_dir(self):
        return self._gitautosync._repo_dir
