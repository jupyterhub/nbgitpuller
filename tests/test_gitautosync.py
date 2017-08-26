import os
import shutil
import subprocess
import random
import string
from gitautosync import GitAutoSync


class TestGitAutoSync:

    _gitautosync = None
    _dir_name = 'test-repo'

    def setUp(self):
        self._gitautosync = GitAutoSync(
            'https://github.com/data-8/test-homework',
            'master',
            self._dir_name
        )
        self._delete_init_path()
        for line in self._gitautosync._initialize_repo():
            print(line)

    def test_initialize_repo(self):
        self.setUp()
        assert os.path.exists(self._gitautosync.repo_dir)
        assert os.path.exists(os.path.join(self._gitautosync.repo_dir, ".git"))
        assert self._get_current_branch() == self._gitautosync.branch_name

    def test_get_sub_cwd(self):
        self.setUp()
        result = self._gitautosync.repo_dir
        print("Repo Path w/ CWD:", result)
        assert os.path.exists(result) or not os.path.exists(self._gitautosync.repo_dir)

    def test_repo_is_dirty(self):
        self.setUp()
        result = self._gitautosync.repo_is_dirty()
        assert not result

        self._make_repo_dirty()

        result = self._gitautosync.repo_is_dirty()
        assert result

    def test_make_commit(self):
        self.setUp()
        self._make_repo_dirty()
        for line in self._gitautosync._make_commit():
            print(line)

        assert self._get_latest_commit_msg() == 'WIP'

        result = self._gitautosync.repo_is_dirty()
        assert not result

    def test_save_local_changes(self):
        self.setUp()
        self._make_repo_dirty()
        for line in self._gitautosync._make_commit():
            print(line)

        assert self._get_latest_commit_msg() == 'WIP'

        result = self._gitautosync.repo_is_dirty()
        assert not result

    def test_pull_and_resolve_conflicts(self):
        self.setUp()
        self._retains_new_files()

        assert 'ahead' in self._get_git_status_msg()

    def test_update_repo(self):
        self.setUp()
        self._make_repo_dirty()
        for line in self._gitautosync._update_repo():
            print(line)
        assert self._get_latest_commit_msg() == 'WIP'

        result = self._gitautosync.repo_is_dirty()
        assert not result

        self._retains_new_files()

        assert 'ahead' in self._get_git_status_msg()

    def test_pull_from_remote(self):
        self.setUp()
        self._delete_init_path()
        self._gitautosync.pull_from_remote()

        self.test_initialize_repo()

        self._make_repo_dirty()

        for line in self._gitautosync.pull_from_remote():
            print(line)
        assert self._get_latest_commit_msg() == 'WIP'

        result = self._gitautosync.repo_is_dirty()
        assert not result

        self._retains_new_files()

        assert 'ahead' in self._get_git_status_msg()

    def test_pull_deleted_files(self):
        self.setUp()
        deleted_file_name = '{}/README.md'.format(self._gitautosync.repo_dir)
        subprocess.check_call(['rm', deleted_file_name])

        for line in self._gitautosync._reset_deleted_files():
            print(line)
        assert os.path.exists(deleted_file_name)

    def test_merge_modified_vs_deleted_upstream(self):
        self.setUp()
        cwd = self._gitautosync.repo_dir

        # remove the upstream commit that deletes 'new-file.txt'
        subprocess.check_call(['git', 'reset', '--hard', 'HEAD^'], cwd=cwd)

        # modify 'new-file.txt' locally
        with open(os.path.join(self._dir_name, 'new-file.txt'), 'w') as file:
            file.write('after')

        for line in self._gitautosync.pull_from_remote():
            print(line)
        print(self._get_git_status_msg())
        assert 'ahead' in self._get_git_status_msg()

    def _generate_random_string(self, N):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

    def _get_latest_commit_msg(self):
        cwd = self._gitautosync.repo_dir
        ps = subprocess.Popen(['git', 'log', '--oneline'], stdout=subprocess.PIPE, cwd=cwd)
        output = subprocess.check_output(['head', '-n', '1'], stdin=ps.stdout, cwd=cwd)
        ps.wait()
        return output.decode('utf-8').strip().split(' ')[1]

    def _get_current_branch(self):
        cwd = self._gitautosync.repo_dir
        out = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=cwd)
        return out.decode('utf-8').strip()

    def _create_new_file(self, name):
        with open(self._gitautosync.repo_dir + "/" + name, 'w') as new_file:
            new_file.write(self._generate_random_string(10))

    def _get_git_status_msg(self):
        cwd = self._gitautosync.repo_dir
        return subprocess.check_output(['git', 'status'], cwd=cwd).decode('utf-8')

    def _make_repo_dirty(self):
        new_file_name = "{}/README.md".format(self._gitautosync.repo_dir)
        with open(new_file_name, 'w') as file:
            file.write(self._generate_random_string(10))

    def _delete_init_path(self):
        if os.path.exists(self._gitautosync.repo_dir):
            shutil.rmtree(self._gitautosync.repo_dir)

    def _retains_new_files(self):
        self._create_new_file("new_file1.txt")

        for line in self._gitautosync._make_commit():
            print(line)

        self._create_new_file("new_file2.txt")

        for line in self._gitautosync._pull_and_resolve_conflicts():
            print(line)

        assert os.path.exists(self._gitautosync.repo_dir + "/new_file2.txt")
        assert os.path.exists(self._gitautosync.repo_dir + "/new_file1.txt")
