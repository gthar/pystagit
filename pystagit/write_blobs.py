#!/usr/bin/env python
"""write blobs as file/x.html and return metadata"""

import itertools
import os
import stat

import markdown
import pygit2
import pygments
from pygments import lexers, formatters

from pystagit.common import write_output


def pick_lexer(filename, contents):
    """chose an appropriate pygments lexer based on filename an contents"""
    if filename in ["LICENSE", "COPYING", "README"]:
        return lexers.TextLexer()
    try:
        return lexers.guess_lexer_for_filename(filename, contents)
    except pygments.util.ClassNotFound:
        try:
            return lexers.guess_lexer(contents)
        except pygments.util.ClassNotFound:
            return lexers.TextLexer()


def highlight(contents, lexer):
    """syntax highlighting using pygments"""
    formatter = formatters.HtmlFormatter(
        linenos="table", lineanchors="loc", anchorlinenos=True
    )
    return pygments.highlight(contents, lexer, formatter)


def get_filetype(filemode):
    """get the filetype of a file mode"""
    mode_funcs = [
        (stat.S_ISREG, "-"),
        (stat.S_ISBLK, "b"),
        (stat.S_ISCHR, "c"),
        (stat.S_ISDIR, "d"),
        (stat.S_ISFIFO, "p"),
        (stat.S_ISLNK, "l"),
        (stat.S_ISSOCK, "s"),
    ]
    for pred, val in mode_funcs:
        if pred(filemode):
            return val
    return "?"


def get_perms(filemode):
    """get the permissions string"""
    perm_vals = [
        (stat.S_IRUSR, "r"),
        (stat.S_IWUSR, "w"),
        (stat.S_IXUSR, "x"),
        (stat.S_IRGRP, "r"),
        (stat.S_IWGRP, "w"),
        (stat.S_IXGRP, "x"),
        (stat.S_IROTH, "r"),
        (stat.S_IWOTH, "w"),
        (stat.S_IXOTH, "x"),
    ]
    perms = (perm if filemode & val else "-" for val, perm in perm_vals)
    return "".join(perms)


def add_bits_info(perms, filemode):
    """add info related to the set UID bit, the set GID bit and the sticky
    bit"""
    bit_vals = [
        (stat.S_ISUID, 2, "s", "s"),
        (stat.S_ISGID, 5, "s", "s"),
        (stat.S_ISVTX, 8, "t", "T"),
    ]
    for bit, i, xval, yval in bit_vals:
        if filemode & bit:
            if perms[i] == "x":
                perms[i] = xval
            else:
                perms[i] = yval
    return perms


def format_filemode(filemode):
    """format a filemode int into a a nice string"""
    filetype = get_filetype(filemode)
    permissions = add_bits_info(get_perms(filemode), filemode)
    return filetype + permissions


def write_blob(blob, header_data, path, levels):
    """write html displaying a blob"""
    if path is None:
        path = ""

    try:
        os.makedirs(os.path.join("file", path))
    except FileExistsError:
        pass

    try:
        os.makedirs(os.path.join("raw", path))
    except FileExistsError:
        pass
    
    if blob.is_binary:
        content = None
        highlighted = None
        rendered = None
        nlines = 0
    else:
        content = blob.data.decode()
        nlines = len(content.strip().split("\n"))

        lexer = pick_lexer(blob.name, content)
        highlighted = highlight(content, lexer)

        if isinstance(lexer, lexers.MarkdownLexer):
            rendered = markdown.markdown(
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
        else:
            rendered = None

    data = {
        "size": blob.size,
        "name": blob.name,
        "mode": format_filemode(blob.filemode),
        "full_name": os.path.join(path, blob.name),
        "binary": blob.is_binary,
        "nlines": nlines,
    }

    write_output(
        template="file.html",
        outfile=f"file/{path}/{blob.name}.html",
        content=highlighted,
        rendered=rendered,
        name=blob.name,
        header=header_data,
        rootpath="/".join([".."] * levels),
        file=data,
    )

    raw_path = os.path.join("raw", path, blob.name)
    with open(raw_path, "wb") as out_fh:
        out_fh.write(blob.data)

    return data


def write_file_tree(node, header_data, path=None, levels=0):
    """recursevily read the files in a tree"""

    if path is not None:
        name = os.path.join(path, node.name)
    else:
        name = node.name

    if isinstance(node, pygit2.Blob):
        return [write_blob(node, header_data, path=path, levels=levels)]

    if isinstance(node, pygit2.Tree):
        subnodes = list(
            itertools.chain.from_iterable(
                write_file_tree(
                    subnode, header_data, path=name, levels=levels + 1
                )
                for subnode in node
            )
        )
        return subnodes

    return []
