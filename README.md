# git-shadow

git-shadow transparently records coding activity between commits in near-real-time. Recorded activity is stored into per-commit git repositories that can be analyzed with existing git workflows.

# Example: Determining *exactly* when you injected a silly bug in your code

1. A silly bug is found in your code during a code review, or worse...

![goto fail](https://foote.pub/images/goto-fail.png)

2. Find commit for bug using conventional weapons

```
foote$ git log -S 'goto fail'
commit 7dba55fb8590f043afe935a9b366814fa5727804
Author: Jonathan Foote <jmfoote@loyola.edu>
Date:   Mon Jan 23 10:03:49 2014 -0500

    Fixed issue #PR59241

commit a4c55a248e8ad381d71466c0a8e3a477dfe5ac60
Author: Steve Jobs <steve@apple.com>
Date:   Fri June 11 14:00:55 2003 -0500

    Initial commit
```

We can see from the above pickaxe search that the only commits that added or removed a `goto fail` were the initial commit and commit `7dba55f...` made by this shady `Jonathan Foote` character.

3. Find exact minute/second you made the mistake using `git-shadow`

```
$ git checkout 7dba55fb8590f043afe935a9b366814fa5727804
Note: checking out '7dba55fb8590f043afe935a9b366814fa5727804'.
[...]

HEAD is now at 7dba55f... Fixed issue #PR59241
flan:demo user0$ git shadow log -S 'goto fail'
commit 69136d46fe975e9b239de44d330eaba3d4593665
Author: Jonathan Foote <jmfoote@loyola.edu>
Date:   Fri Jan 20 23:12:54 2014 -0500

    'file_modified'

commit 38013a4f169e3e8d4c8208d9cf65507559c95f29
Author: Jonathan Foote <jmfoote@loyola.edu>
Date:   Thu Jan 19 14:12:00 2014 -0500

    '7dba55fb8590f043afe935a9b366814fa5727804'
```

The oldest shadow commit discovered above, `38013a4...` is the verbatim shadow copy of the code created when I first started working on the `PR59241`. According to pickaxe, the only other shadow commit to modify `goto fail` was `69136d4...` made at `Fri Jan 20 23:12:54 2014 -0500`. Looks like I was coding late at night when I made the mistake...

4. Query big brother to do a root cause analysis

![tweet](https://foote.pub/images/goto-fail-tweet.png)

5. Change your coding habits to avoid making the same mistake again

**Disclaimer**: I had nothing to do with the real `goto fail;` bug, I've never worked for Apple, and I have no idea how the bug was actually introduced. IOW, relax, it's just an example.

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

# How it works

When `git shadow activate` is invoked, a mirror of all files that are tracked in the current repo is created in `<repo path>/.shadow`. Hooks are added to the current repo to keep the shadow consistent with HEAD. 

As you code in vim, the `vim-shadow` plugin periodically passes the contents of the active buffer to the `git-shadow shadow-file` command, which adds them to a shadow git repository inside the `.shadow` directory. Note that while this proof-of-concept uses vim, any editor that can be coerced into running `git-shadow` when buffer contents change could be used.

As commits are made to your codebase, `git-shadow` catalogues git repositories containing your coding activity in the `.shadow` directory by commit id. The `.shadow` directory contains a directory for each commit id that `git-shadow` has been active for, including `current`. 

Running `git shadow <git cmd>` simply runs the corresponding git command as if it were invoked from in `.shadow/current`.

# Warnings

This is a proof of concept. There is no support for history re-writing (and probably a lot of other cases I haven't got to yet). Re-ordering may work, but squashing/splitting, filter-branch, etc. almost certainly will not. 
