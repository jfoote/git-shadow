# git-shadow

git-shadow transparently records coding activity between commits in near-real-time. Recorded activity is stored into per-commit git repositories that can be analyzed with existing git workflows.

# Usage (vim)

### Installation 

Clone the git repo

```
$ git clone https://github.com/jfoote/git-shadow
```

Put `git-shadow` on your path

```
$ pushd git-shadow && ln -s `pwd`/git-shadow /usr/local/bin/git-shadow && popd
```

Configure vim to autoload `vim-shadow`

```
$ pushd git-shadow && ln -s `pwd`/vim-shadow ~/.vim/bundle
```

### Coding 

Change directories to a git repo

```
$ cd demo
```

Run `git shadow activate`

```
$ git shadow activate
```

Code with vim

```
$ vim main.c
```

### Analysis

Checkout an interesting commit (ex: where a bug was introduced)

```
$ git checkout 7dba55fb8590f043afe935a9b366814fa5727804
```

Run git analysis the shadow repository via `git shadow <git command>`, or access the repo directly at `<repo>/.shadow/current`

```
$ git shadow log -S 'goto fail'
```

# Fictional Example

Say a silly bug is found in my code during an internal code review, or worse...

![goto fail](http://foote.pub/images/goto-fail.png)

... and I decide to do some root-cause analysis with the help of `git-shadow`

**Gratuitous Disclaimer**: I had nothing to do with the real `goto fail;` bug, I've never worked for Apple, and I have no idea how the bug was actually introduced. IOW, it's just an example.

### 1. Find the commit where the bug was injected using conventional methods 

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

I can see from the above pickaxe search that the only commits that added or removed a `goto fail` were the initial commit and commit `7dba55f...` made by this shady `Jonathan Foote` character.

### 2. Find exact minute/second you made the mistake using `git-shadow`

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

### 3. Query your big data using the fault injection time to do a root cause analysis

![tweet](http://foote.pub/images/goto-fail-tweet.png)

Oh. Yeah. Probably shouldn't have done any programming that Friday night.

*Note: Drunk tweets notwithstanding, querying something like [fluxtream](https://fluxtream.org/) could provide some novel insight.*

### 4. I change my habits to avoid making the same mistake again. 

I use `git-shadow` to continuously improve my programming skills, becoming to envy of all my friends. After a few years of flawless programming, I retire as a rich philantropist.


# How it works

When `git shadow activate` is invoked, a mirror of all files that are tracked in the current repo is created in `<repo path>/.shadow`. Hooks are added to the current repo to keep the shadow consistent with HEAD. 

All of the shadow logic is implemented in a single python script (`git-shadow`). The example editor plugin is implemented in two simple vimscript files (`vim-shadow/autoload/shadow.vim` and `vim-shadow/plugin/shadow.vim`).

## Coding

As you code in vim, the `vim-shadow` plugin periodically passes the contents of the active buffer to the `git-shadow shadow-file` command, which adds them to a shadow git repository inside the `.shadow` directory. Note that while this proof-of-concept uses vim, any editor that can be coerced into running `git-shadow` when buffer contents change could be used.

![flow1](http://foote.pub/images/shadow1.png)

As commits are made to your codebase, `git-shadow` catalogues git repositories containing your coding activity in the `.shadow` directory by commit id. The `.shadow` directory contains a directory for each commit id that `git-shadow` has been active for, including `current`. 

## HEAD changes

When the user runs a `checkout` command, a hook placed in `.git/hooks` when the user ran the `git shadow activate` command deletes the existing `.shadow/current` and replaces it with the directory corresponding to the new `HEAD` if it exists.

![flow3](http://foote.pub/images/shadow3.png)

The hook simply calls an incantation of `git-shadow` -- all of the hook logic is contained in the `git-shadow` script. *Note: This logic probably needs some work.*

## Analysis

Running `git shadow <git cmd>` simply runs the corresponding git command as if it were invoked from `.shadow/current`.

![flow2](http://foote.pub/images/shadow2.png)

# Warnings

I've got plans to beat on this, but I haven't done it yet. This script is simply a proof of concept. There is no support for history re-writing (and probably a lot of other `git` use cases). Re-ordering may work, but squashing/splitting, filter-branch, etc. almost certainly will not. 

```
Jonathan Foote
jmfoote@loyola.edu
24 Jan 2014
```
