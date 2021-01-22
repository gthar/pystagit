#!/usr/bin/env python
"""functions to write commits in commit/x.html and return data for log.html"""

import os

from pystagit.common import fmt_time, write_output


EMPTY_TREE_ID = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def build_deltastrs(addcount, delcount):
    """build a string of `+`s and `-`s representing a delta"""
    strlen = 79
    changed = addcount + delcount
    if changed > strlen:
        if addcount > 0:
            addcount = round(strlen / changed * addcount)
        if delcount > 0:
            delcount = round(strlen / changed * delcount)
    return "+" * addcount, "-" * delcount


def get_line_data(line):
    """get the data from a line"""
    if line.old_lineno == -1:
        status = "i"
    elif line.new_lineno == -1:
        status = "d"
    else:
        status = None
    return {"status": status, "content": line.content}


def get_hunk_data(hunk):
    """get the desired data from a hunk"""
    line_info = list(map(get_line_data, hunk.lines))
    addcount = len([line for line in line_info if line["status"] == "i"])
    delcount = len([line for line in line_info if line["status"] == "d"])
    return {
        "addcount": addcount,
        "delcount": delcount,
        "header": hunk.header,
        "lines": line_info,
    }


def get_delta_stats(patch):
    """get info for a delta"""
    delta = patch.delta

    hunks_info = list(map(get_hunk_data, patch.hunks))

    addcount = sum(hunk["addcount"] for hunk in hunks_info)
    delcount = sum(hunk["delcount"] for hunk in hunks_info)
    addstr, delstr = build_deltastrs(addcount, delcount)

    return {
        "status": delta.status_char(),
        "old_file": delta.old_file.path,
        "new_file": delta.new_file.path,
        "addcount": addcount,
        "delcount": delcount,
        "total": addcount + delcount,
        "addstr": addstr,
        "delstr": delstr,
        "hunks": hunks_info,
    }


def write_commits(commit, repo, header_data):
    """write commits in commit/x.html and return data for log.html"""

    try:
        os.makedirs("commit")
    except FileExistsError:
        pass

    try:
        parent_id = commit.parent_ids[0]
    except IndexError:
        # this should be the first commit, so diff with empty tree
        diff = repo.diff(EMPTY_TREE_ID, commit.id)
        parent_id = None
    else:
        diff = repo.diff(parent_id, commit.id)
    stats = diff.stats

    commit_info = {
        "id": commit.id,
        "parent_id": parent_id,
        "date": fmt_time(commit.author.time),
        "published_date": fmt_time(commit.author.time, "iso"),
        "updated_date": fmt_time(commit.committer.time, "iso"),
        "full_date": fmt_time(
            commit.author.time, "full", commit.author.offset
        ),
        "msg": commit.message.strip(),
        "author": commit.author.name,
        "email": commit.author.email,
        "filecount": stats.files_changed,
        "addcount": stats.insertions,
        "delcount": stats.deletions,
    }

    deltas_info = list(map(get_delta_stats, diff))

    write_output(
        template="commit.html",
        outfile=f"commit/{commit.id}.html",
        name=commit_info["msg"],
        header=header_data,
        commit=commit_info,
        deltas=deltas_info,
        rootpath="..",
    )

    return commit_info
