#!/usr/bin/env python

import argparse;
import os
import subprocess
import sys
from collections import defaultdict

ignored_tags = "build,chore,ci,docs,test".split(',')


def main(*args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_file", type=str, default='CHANGELOG.md', help="Output file")
    parser.add_argument("--tag_pattern", type=str, default="v*", help="Pattern to match tags")
    parser.add_argument("--repo", type=str, default="ctc-oss/fapolicy-analyzer", help="GitHub repo")
    parser.add_argument("--ignores", type=str, default=".ignoredchanges", help="List of shas to exclude from log")
    args = parser.parse_args(args)

    ignored_commits = []
    if os.path.exists(args.ignores):
        with open(args.ignores, "r") as f:
            ignored_commits = f.read().splitlines()

    print(f'# Changelog\n')

    tags = git("tag", "-l", args.tag_pattern).splitlines()
    tags.reverse()
    for i in range(len(tags) - 1):
        tag, prev = tags[i:i + 2]
        when = git("log", tag, "-n1", "--format=%as")

        authors = defaultdict(int)
        log = gitlog("--format=%h,%H,%an,%s", f"{prev}..{tag}").splitlines()

        commits = list()
        for entry in log:
            short, long, author, title = entry.split(',', 4)
            if long not in ignored_commits and not ignored_commit(title):
                commits.append(f"[{short}](https://github.com/{args.repo}/commit/{long}) {title} [{author}]")
                authors[author] = authors[author] + 1

        if commits:
            author_list = list(authors.keys())
            author_list.sort()

            print(f'## {tag} ({when})\n')
            for commit in commits:
                print(f"  - {commit}")
            print("### Contributors\n")
            for author in author_list:
                print(f"  - {author}")


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True).stdout.decode("utf-8").strip()


def gitlog(*args):
    fullargs = ["--no-pager", "log", "--no-merges"] + list(args)
    return git(*fullargs)


def ignored_commit(title):
    tag = title.split(':', 1)[0]
    return tag in ignored_tags


if __name__ == "__main__":
    main(*sys.argv[1:])
