# git-shadow

git-shadow transparently records coding activity between commits in near-real-time. Recorded activity is stored in git repositories and can be analyzed with existing git workflows.

# Installation (vim)

1. Clone the git repo

2. Put `git-shadow` on your path

3. Configure vim to autoload `vim-shadow`

# Usage (vim)

1. Change directories to a git repo

2. Run `git shadow activate`

3. Code with vim

## Analysis

1. Checkout an interesting commit (ex: where a bug was introduced)

2. Run git analysis the shadow repository via `git shadow <git command>`, or access the repo directly at `<repo>/.shadow/current`

## How it works

When `git shadow activate` is invoked, a mirror of all files that are tracked in the current repo is created in `<repo path>/.shadow`. As you code in vim, the `vim-shadow` plugin passes the contents of the active buffer to the `git-shadow` command, which adds them to a shadow git repository inside the `.shadow` directory.

As commits are made to your codebase, `git-shadow` catalogues git repositories containing your coding activity in the `.shadow` directory.

# Warnings

This is a proof of concept. There is no support for history re-writing. Re-ordering may work, but squashing/splitting, filter-branch, etc. almost certainly will not. 
