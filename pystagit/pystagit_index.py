#!/usr/bin/env python
"""Build an index.html for the repos"""

# todo: sort by modification date

import sys
import os

import pygit2

from pystagit.common import (
    get_name,
    read_repo_info,
    fmt_time,
    sorter,
    write_output,
)


def repo_info(path):
    """get the desired data from a path containing a repo"""
    abs_path = os.path.realpath(path)
    try:
        repo = pygit2.Repository(abs_path)
    except pygit2.GitError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    vals = {
        "name": get_name(abs_path),
        "desc": read_repo_info(abs_path, "description"),
        "owner": read_repo_info(abs_path, "owner"),
        "date": fmt_time(repo[repo.head.target].author.time),
    }
    return {k: v for k, v in vals.items() if v is not None}


def main():
    """render the index.html for the repos"""
    repos_data = sorter(list(map(repo_info, sys.argv[1:])))
    write_output(template="index.html", outfile=sys.stdout, repos=repos_data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
