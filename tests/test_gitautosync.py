import os
import shutil
import subprocess
import random
import string
from gitautosync.gitautosync import GitAutoSync


class TestGitAutoSync(object):

    _gitautosync = None

    def setUp(self):
        self._gitautosync = GitAutoSync(
            'https://github.com/data-8/test-homework',
            'gh-pages',
            'test-repo'
        )
        self._delete_init_path()
        self._gitautosync._initialize_repo()

    def test_initialize_repo(self):
        self.setUp()
        assert os.path.exists(self._get_repo_dir())
        assert os.path.exists(os.path.join(self._get_repo_dir(), ".git"))

    def test_get_sub_cwd(self):
        self.setUp()
        result = self._gitautosync._get_sub_cwd()
        print("Repo Path w/ CWD:", result)
        assert os.path.exists(result) or not os.path.exists(self._get_repo_dir())

    def test_repo_is_dirty(self):
        self.setUp()
        result = self._gitautosync._repo_is_dirty()
        assert not result

        self._make_repo_dirty()

        result = self._gitautosync._repo_is_dirty()
        assert result

    def test_make_commit(self):
        self.setUp()
        self._make_repo_dirty()
        self._gitautosync._make_commit()

        assert self._get_latest_commit_msg() == 'WIP'

        result = self._gitautosync._repo_is_dirty()
        assert not result

    def test_pull_and_resolve_conflicts(self):
        self.setUp()
        self._retains_new_files()

        assert 'ahead' in self._get_git_status_msg()

    def test_update_repo(self):
        self.setUp()
        self._make_repo_dirty()
        self._gitautosync._update_repo()
        assert self._get_latest_commit_msg() == 'WIP'

        result = self._gitautosync._repo_is_dirty()
        assert not result

        self._retains_new_files()

        assert 'ahead' in self._get_git_status_msg()

    def test_pull_from_remote(self):
        self.setUp()
        self._delete_init_path()
        self._gitautosync.pull_from_remote()

        self.test_initialize_repo()

        self._make_repo_dirty()

        self._gitautosync.pull_from_remote()
        assert self._get_latest_commit_msg() == 'WIP'

        result = self._gitautosync._repo_is_dirty()
        assert not result

        self._retains_new_files()

        assert 'ahead' in self._get_git_status_msg()

    def test_pull_deleted_files(self):
        self.setUp()
        deleted_file_name = '{}/README.md'.format(self._get_repo_dir())
        subprocess.check_call(['rm', deleted_file_name])
        self._gitautosync._reset_deleted_files()
        assert os.path.exists(deleted_file_name)

    def _generate_random_string(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

    def _get_latest_commit_msg(self):
        cwd = self._gitautosync._get_sub_cwd()
        ps = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE, cwd=cwd)
        output = subprocess.check_output(['head', '-n', '1'], stdin=ps.stdout, cwd=cwd)
        ps.wait()
        return output.decode('utf-8').strip().split(' ')[1]

    def _create_new_file(self, name):
        with open(self._get_repo_dir() + "/" + name, 'w') as new_file:
            new_file.write(self._generate_random_string(10))

    def _get_git_status_msg(self):
        cwd = self._gitautosync._get_sub_cwd()
        return subprocess.check_output(['git', 'status'], cwd=cwd).decode('utf-8')

    def _make_repo_dirty(self):
        new_file_name = "{}/README.md".format(self._get_repo_dir())
        with open(new_file_name, 'w') as file:
            file.write(self._generate_random_string(10))

    def _delete_init_path(self):
        if os.path.exists(self._get_repo_dir()):
            shutil.rmtree(self._get_repo_dir())

    def _retains_new_files(self):
        self._create_new_file("new_file1.txt")

        self._gitautosync._make_commit()

        self._create_new_file("new_file2.txt")

        self._gitautosync._pull_and_resolve_conflicts()

        assert os.path.exists(self._get_repo_dir() + "/new_file2.txt")
        assert os.path.exists(self._get_repo_dir() + "/new_file1.txt")

    def _get_repo_dir(self):
        return self._gitautosync._repo_dir
