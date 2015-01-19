#!/usr/bin/env python

from unittest import TestCase
import subprocess

def rm_r(path):
    import os, shutil
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)

class Test_git_shadow(TestCase):
    def setUp(self):
        import tempfile
        self.repo_dir = tempfile.mkdtemp()
        subprocess.check_call(["git", "init", self.repo_dir])

    def tearDown(self):
        rm_r(self.repo_dir)

    def test_activate(self):
        import sys, os
        print sys.path
        subprocess.call(["./git-shadow", "activate", self.repo_dir])

        # verify git repo was initialized
        self.assertTrue(os.path.exists(os.path.join(self.repo_dir, ".shadow", ".git")))

        # verify hooks were installed in parent repository

