#!/usr/bin/env python

import sys, os, subprocess, shlex, time, shutil, filecmp

def help_exit():
    sys.stderr.write("usage: ./git_shadow.py [full path to file w/ git-shadow file extension]\n")
    sys.exit(-1)

def get_branch(path):
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    text = subprocess.check_output(["git", "branch"], cwd=path)
    line = [l for l in text.splitlines() if "*" in l][0]
    return line.strip("* ")

def get_repo_path(path):
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    return subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=path).strip()

def get_filepath_relative_to_repo(filepath):
    dirpath, filename = os.path.split(filepath)
    repo_rel_dirpath = subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=dirpath).strip()
    return os.path.join(repo_rel_dirpath, filename)

def commit(src, dst):
    commit_id = subprocess.check_output(["git", "log", '--format=%H', "-n", "1"], cwd=src).strip()
    subprocess.check_call(["git", "commit", "-m" "'%s'" % commit_id], cwd=dst)

def shadow_controlled_files(src, branch, dst):
    rel_fps = subprocess.check_output(["git", "ls-tree", "-r", branch, "--name-only"], cwd=src).strip().splitlines()
    changed = False
    for rel_fp in rel_fps:
        dst_filepath = os.path.join(dst, rel_fp)
        dst_dirpath, dst_filename = os.path.split(dst_filepath)
        src_filepath = os.path.join(src, rel_fp)
        try:
            if not os.path.exists(dst_dirpath):
                subprocess.check_call(["mkdir", "-p", dst_dirpath], cwd=src)
            shutil.copy(src_filepath, dst_filepath)
            subprocess.check_call(["git", "add", dst_filepath], cwd=dst)
            log("added", dst_filepath)
            changed = True
        except Exception as e:
            log("error copying %s to %s, probably uncommitted 'git mv'" % (src_filepath, dst_filepath))
            logging.exception(e)
    if changed:
        commit(src, dst)

import logging
def log(*args):
    logging.debug(" ".join([str(i) for i in args]))

if __name__=="__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        help_exit()

    temp_filepath = sys.argv[1]
    if not os.path.exists(temp_filepath):
        help_exit()

    shadow_home_dir = os.path.expanduser(os.path.join("~", ".git-shadow"))
    if not os.path.exists(shadow_home_dir):
        subprocess.check_call(["mkdir", "-p", shadow_home_dir])
        
    log_path = os.path.join(shadow_home_dir, "log.txt")
    logging.basicConfig(filename=log_path, level=logging.DEBUG)

    filepath = temp_filepath[:-len(".shadow.2014-12-03_13:48:39")]
    dirpath, filename = os.path.split(filepath)
    try:
        branch = get_branch(dirpath)
    except subprocess.CalledProcessError:
        #log("not a git repo")
        os.remove(temp_filepath)
        sys.exit(0)

    try:
        # calculate directories and paths
        repo_path = get_repo_path(dirpath)
        shadow_repo_path = os.path.join(shadow_home_dir, repo_path[1:])
        shadow_dirpath = os.path.join(shadow_repo_path, branch, os.path.dirname(get_filepath_relative_to_repo(filepath)))
        shadow_filepath = os.path.join(shadow_dirpath, filename)

        if not os.path.exists(shadow_repo_path):
            # first time tracking this repo; shadow all files
            subprocess.call(["mkdir", "-p", shadow_repo_path]) 
            subprocess.call(["git", "init", shadow_repo_path])
            shadow_controlled_files(repo_path, branch, shadow_dirpath)

        if not os.path.exists(shadow_filepath):
            #log(shadow_filepath, "not under version control")
            os.remove(temp_filepath)
            sys.exit(0)
    
        if filecmp.cmp(temp_filepath, shadow_filepath):
            #log("no changes to", filepath)
            os.remove(temp_filepath)
            sys.exit(0)
    
        # copy file in
        shutil.copy(temp_filepath, shadow_filepath)
        os.remove(temp_filepath)
    
        # commit it
        subprocess.check_call(["git", "add", shadow_filepath], cwd=shadow_dirpath)
        commit(repo_path, shadow_repo_path)
        #log("commited changes to", shadow_filepath)
        sys.exit(0)
    except Exception as e:
        log("otherwise unhandled error")
        logging.exception(e)
        log("filepath", filepath)
        log("dirpath", dirpath)
        log("shadow_repo_path", shadow_repo_path)
        log("shadow_dirpath", shadow_dirpath)
        log("shadow_filepath", shadow_filepath)
        sys.exit(-2)
