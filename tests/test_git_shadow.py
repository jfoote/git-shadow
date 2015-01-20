#!/usr/bin/env python

from unittest import TestCase
import subprocess, os, shutil, tempfile

# Load git-shadow as a module for functional unit tests. Le Hack. Sacrebleu!!1
import imp
git_shadow = imp.load_source("git_shadow", os.path.join(os.getcwd(), "git-shadow")) 

def rm_r(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)

def num_commits(repo_dir):
    out = subprocess.check_output(["git", "log", "--format=%H"], cwd=repo_dir)
    return len(out.strip().splitlines())

class UnitTests(TestCase):

    def setUp(self):
        # create dummy repo for testing
        self.repo_dir = os.path.realpath(tempfile.mkdtemp())
        subprocess.check_call(["git", "init", self.repo_dir])

        # add cwd to path to support execution of "git-shadow" in tests
        self.env = os.environ
        self.env["PATH"] = ":".join(self.env["PATH"].split(":") + [os.getcwd()])

    def tearDown(self):
        rm_r(self.repo_dir)

    def test_get_shadow_repo_path(self):
        '''
        Verify the shadow repo path is constructed properly and that an 
        Exception is raised if the func is called outside a git repo.
        '''
        p = git_shadow.get_shadow_repo_path(self.repo_dir)

        self.assertEqual(git_shadow.get_shadow_repo_path(self.repo_dir),
                os.path.join(self.repo_dir, ".shadow"))

        tdir = tempfile.mkdtemp()
        try:
            with self.assertRaises(subprocess.CalledProcessError):
                git_shadow.get_shadow_repo_path(tdir)
        finally:
            rm_r(tdir)

    def test_create_shadow_repo(self):
        '''
        Verify the function creates repos properly and throws an Exception if
        the repo already exists/force is False
        '''
        git_shadow.create_shadow_repo(cwd=self.repo_dir, force=False)
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".shadow")))

        with self.assertRaises(RuntimeError):
            git_shadow.create_shadow_repo(cwd=self.repo_dir, force=False)

        git_shadow.create_shadow_repo(cwd=self.repo_dir, force=True)
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".shadow")))

    def test_delete_shadow_repo(self):
        '''
        Verify the function deletes a shadow repo properly and throws an 
        Exception if the shadow repo doesn't exist
        '''
        with self.assertRaises(RuntimeError):
            git_shadow.delete_shadow_repo(self.repo_dir)

        git_shadow.create_shadow_repo(cwd=self.repo_dir, force=True)
        git_shadow.delete_shadow_repo(self.repo_dir)
        self.assertFalse(os.path.exists(os.path.join(self.repo_dir, ".shadow")))

    def test_add_hooks(self):
        # verify hooks are installed in parent repository
        subprocess.call(["git", "shadow", "add-hooks", self.repo_dir], env=self.env)
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".git", "hooks", "pre-commit")))
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".git", "hooks", "post-commit")))
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".git", "hooks", "pre-checkout")))

    def test_remove_hooks(self):
        # verify hooks are removed from parent repository
        subprocess.call(["git", "shadow", "add-hooks", self.repo_dir], env=self.env)
        subprocess.call(["git", "shadow", "remove-hooks", self.repo_dir], env=self.env)
        self.assertFalse(os.path.exists(os.path.join(self.repo_dir, ".git", "hooks", "pre-commit")))
        self.assertFalse(os.path.exists(os.path.join(self.repo_dir, ".git", "hooks", "post-commit")))
        self.assertFalse(os.path.exists(os.path.join(self.repo_dir, ".git", "hooks", "pre-checkout")))

        # verify git-shadow hooks are removed without clobbering existing hook file
        filetext = "foobaz"
        filepath = os.path.join(self.repo_dir, ".git", "hooks", "pre-commit")
        open(filepath, "wt").write(filetext)
        subprocess.call(["git", "shadow", "add-hooks", self.repo_dir], env=self.env)
        subprocess.call(["git", "shadow", "remove-hooks", self.repo_dir], env=self.env)
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".git", "hooks", "pre-commit")))
        self.assertEqual(filetext, open(filepath, "rt").read())
        self.assertFalse(os.path.exists(os.path.join(self.repo_dir, ".git", "hooks", "post-commit")))
        self.assertFalse(os.path.exists(os.path.join(self.repo_dir, ".git", "hooks", "pre-checkout")))

    def test_shadow_controlled_files(self):
        # add some files to test repo
        test_filepath = os.path.join(self.repo_dir, "foobar")
        open(test_filepath, "wt").write("some file contents")
        subprocess.check_call(["git", "add", test_filepath], cwd=self.repo_dir, env=self.env)

        os.mkdir(os.path.join(self.repo_dir, "foobaz"))
        test_filepath = os.path.join(self.repo_dir, "foobaz", "foomanchu")
        open(test_filepath, "wt").write("some other file contents")

        subprocess.check_call(["git", "add", test_filepath], cwd=self.repo_dir, env=self.env)
        subprocess.check_call(["git", "commit", "-m", "'message'"], cwd=self.repo_dir, env=self.env)
        # create shadow
        git_shadow.create_shadow_repo(self.repo_dir)
        git_shadow.shadow_controlled_files(self.repo_dir)
        # verify
        self.assertTrue(os.path.exists(os.path.join(git_shadow.get_shadow_repo_path(self.repo_dir), "foobar")))
        self.assertTrue(os.path.exists(os.path.join(git_shadow.get_shadow_repo_path(self.repo_dir), "foobaz", "foomanchu")))

    def test_activate(self):
        subprocess.call(["git", "shadow", "activate", self.repo_dir], env=self.env)

        # verify git repo was initialized
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".shadow", ".git")))

    def test_shadow_file(self):
        # add some files to a test repo
        test_filepath = os.path.join(self.repo_dir, "foobar")
        open(test_filepath, "wt").write("some file contents")
        subprocess.check_call(["git", "add", test_filepath], cwd=self.repo_dir, env=self.env)

        os.mkdir(os.path.join(self.repo_dir, "foobaz"))
        test_filepath = os.path.join(self.repo_dir, "foobaz", "foomanchu")
        open(test_filepath, "wt").write("some other file contents")

        subprocess.check_call(["git", "add", test_filepath], cwd=self.repo_dir, env=self.env)
        subprocess.check_call(["git", "commit", "-m", "'message'"], cwd=self.repo_dir, env=self.env)

        # create shadow repo
        git_shadow.create_shadow_repo(self.repo_dir)
        git_shadow.shadow_controlled_files(self.repo_dir)

        # baseline number of commits in shadow repo
        shadow_repo_path = git_shadow.get_shadow_repo_path(self.repo_dir)
        commits = num_commits(shadow_repo_path)

        # verify adding an unchanged file doesn't result in a commit to the shadow repo
        git_shadow.shadow_file(test_filepath, test_filepath)
        self.assertEqual(commits, num_commits(shadow_repo_path))

        # verify adding a changed file *does* result in a commit to the shadow repo
        with tempfile.NamedTemporaryFile() as tf:
            tf.write("new contents..\nare here!")
            tf.flush()
            git_shadow.shadow_file(test_filepath, tf.name)
            self.assertEqual(commits+1, num_commits(shadow_repo_path))


class IntegrationTests(TestCase):

    def setUp(self):
        # create dummy repo for testing
        self.repo_dir = os.path.realpath(tempfile.mkdtemp())
        subprocess.check_call(["git", "init", self.repo_dir])

        # add cwd to path to support execution of "git-shadow" in tests
        self.env = os.environ
        self.env["PATH"] = ":".join(self.env["PATH"].split(":") + [os.getcwd()])

    def tearDown(self):
        rm_r(self.repo_dir)

    def test_shadow_file(self):
        # add some files to a test repo
        test_filepath = os.path.join(self.repo_dir, "foobar")
        open(test_filepath, "wt").write("some file contents")
        subprocess.check_call(["git", "add", test_filepath], cwd=self.repo_dir, env=self.env)

        os.mkdir(os.path.join(self.repo_dir, "foobaz"))
        test_filepath = os.path.join(self.repo_dir, "foobaz", "foomanchu")
        open(test_filepath, "wt").write("some other file contents")

        subprocess.check_call(["git", "add", test_filepath], cwd=self.repo_dir, env=self.env)
        subprocess.check_call(["git", "commit", "-m", "'message'"], cwd=self.repo_dir, env=self.env)

        # create shadow repo
        git_shadow.create_shadow_repo(self.repo_dir)
        git_shadow.shadow_controlled_files(self.repo_dir)
        git_shadow.add_hooks(self.repo_dir)

        # simulate a modification to a file and a commit
        open(test_filepath, "wt").write("new contents..\nare here!")
        git_shadow.shadow_file(test_filepath, test_filepath)

        subprocess.check_call(["git", "add", test_filepath], cwd=self.repo_dir, env=self.env)
        subprocess.check_call(["git", "commit", "-m", "'message'"], cwd=self.repo_dir, env=self.env)

        # make sure shadow repo was commited
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".shadow", "git")))
