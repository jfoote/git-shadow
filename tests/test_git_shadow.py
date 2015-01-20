#!/usr/bin/env python

from unittest import TestCase
import subprocess, os, shutil

# Load git-shadow as a module for functional unit tests. Le Hack. Sacrebleu!!1
import imp
git_shadow = imp.load_source("git_shadow", os.path.join(os.getcwd(), "git-shadow")) 

def rm_r(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)

class Test_git_shadow(TestCase):
    def setUp(self):
        # create dummy repo for testing
        import tempfile
        self.repo_dir = tempfile.mkdtemp()
        subprocess.check_call(["git", "init", self.repo_dir])

        # add cwd to path to support execution of "git-shadow" in tests
        self.env = os.environ
        self.env["PATH"] = ":".join(self.env["PATH"].split(":") + [os.getcwd()])

    def tearDown(self):
        rm_r(self.repo_dir)

    def test_activate(self):
        subprocess.call(["git", "shadow", "activate", self.repo_dir], env=self.env)

        # verify git repo was initialized
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".shadow", ".git")))

    def test_create_shadow_repo(self):
        git_shadow.create_shadow_repo(cwd=self.repo_dir, force=False)
        # TODO: stopped here

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
