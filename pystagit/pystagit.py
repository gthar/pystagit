#!/usr/bin/env python
"""Create a static html site from a git repo"""

import os
import sys

import markdown
import pygit2

from pystagit.common import (
    get_name,
    read_repo_info,
    fmt_time,
    sorter,
    write_output,
)
from pystagit.write_commits import write_commits
from pystagit.write_blobs import write_file_tree


LICENSEFILES = ["LICENSE", "LICENSE.md", "COPYING"]
READMEFILES = ["README", "README.md"]


def get_repo_file(repo, flist):
    """try to find the license file"""
    for fname in flist:
        try:
            repo.revparse_single("HEAD:" + fname)
        except KeyError:
            pass
        else:
            return fname


def get_header_data(repo, abs_path):
    """get the data for the headers"""
    result = {
        "name": get_name(abs_path),
        "desc": read_repo_info(abs_path, "description"),
        "url": read_repo_info(abs_path, "url"),
        "license": get_repo_file(repo, LICENSEFILES),
        "readme": get_repo_file(repo, READMEFILES),
        "submodules": get_repo_file(repo, [".gitmodules"]),
    }
    return {k: v for k, v in result.items() if v is not None}


def write_log(commits_data, header_data):
    """write log.html"""
    write_output(
        template="log.html",
        outfile="log.html",
        name="Log",
        header=header_data,
        commits=commits_data,
    )


def write_files(files_data, header_data):
    """write files.html"""
    write_output(
        template="files.html",
        outfile="files.html",
        name="Files",
        header=header_data,
        files=files_data,
    )


def get_ref_info(ref):
    """get the name, author name last commit date from a reference"""
    commit = ref.peel(pygit2.GIT_OBJ_ANY)
    return {
        "name": ref.shorthand,
        "date": fmt_time(commit.author.time),
        "author": commit.author.name,
    }


def write_refs(repo, header_data):
    """write refs.html"""
    refs = repo.references
    refs_info = sorter(
        [
            get_ref_info(refs[refname])
            for refname in refs
            if refname.startswith("refs/heads")
            or refname.startswith("refs/tags")
        ]
    )
    write_output(
        template="refs.html",
        outfile="refs.html",
        name="Refs",
        header=header_data,
        refs=refs_info,
    )


def write_atom(commits_data, header_data):
    """write atom.xml"""
    write_output(
        template="atom.xml",
        outfile="atom.xml",
        header=header_data,
        commits=commits_data,
    )


def write_tags(header_data):
    """write tags.xml"""
    write_output(template="tags.xml", outfile="tags.xml", header=header_data)


def write_about(repo, header_data):
    """write about.html"""
    fname = header_data["readme"]
    head_tree = repo[repo.head.target].tree
    content = head_tree[fname].data.decode()

    render = fname.lower().endswith(".md")
    if render:
        content = markdown.markdown(
            content,
            extensions=[
                "extra",
                "admonition",
                "codehilite",
                "legacy_attrs",
                "legacy_em",
                "meta",
                # "nl2br",
                "sane_lists",
                "smarty",
                "toc",
                "wikilinks",
            ],
        )

    write_output(
        template="about.html",
        outfile="about.html",
        name="about",
        header=header_data,
        content=content,
        rendered=render,
    )


def main():
    """do the thing"""
    repo_dir = sys.argv[1]
    abs_path = os.path.realpath(repo_dir)

    try:
        repo = pygit2.Repository(abs_path)
    except pygit2.GitError as error:
        print(error, file=sys.stderr)
        return 1

    header_data = get_header_data(repo, abs_path)

    if repo.head_is_unborn:
        commits_data = []
        files_data = []

    else:
        head = repo.head.target
        commits_data = [
            write_commits(commit, repo, header_data)
            for commit in repo.walk(head, pygit2.GIT_SORT_TIME)
        ]
        files_data = write_file_tree(repo[head].tree, header_data)

    write_log(commits_data, header_data)
    write_files(files_data, header_data)
    write_refs(repo, header_data)
    write_atom(commits_data, header_data)
    write_tags(header_data)

    if "readme" in header_data:
        write_about(repo, header_data)

    return 0


if __name__ == "__main__":
    sys.exit(main())
