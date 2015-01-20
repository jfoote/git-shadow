#!/usr/bin/env python

from unittest import TestCase
import subprocess, os, shutil
import git_shadow

def rm_r(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)

class Test_git_shadow(TestCase):
    def setUp(self):
        import tempfile
        self.repo_dir = tempfile.mkdtemp()
        subprocess.check_call(["git", "init", self.repo_dir])
        shutil.copyfile("git_shadow.py", "git-shadow")
        subprocess.check_call(["chmod", "+x", "git-shadow"]) # TODO: POSIX only
        self.env = os.environ
        self.env["PATH"] = ":".join(self.env["PATH"].split(":") + [os.getcwd()])

    def tearDown(self):
        os.remove("git-shadow")
        rm_r(self.repo_dir)

    def test_activate(self):
        import sys; print sys.path
        subprocess.call(["git", "shadow", "activate", self.repo_dir], env=self.env)

        # verify git repo was initialized
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".shadow", ".git")))

    def test_create_shadow_repo(self):
        #git_shadow.create_shadow_repo(cwd=cwd, force=True)
        # TODO: stopped here
        pass

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
