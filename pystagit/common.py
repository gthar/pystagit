"""helper functions"""

import os
import pathlib
import re

from datetime import datetime, timezone, timedelta

from jinja2 import FileSystemLoader, Environment, select_autoescape


def get_name(path):
    """get the name from a repo path"""
    return re.sub(r"\.git$", "", os.path.basename(path))


def read_repo_info(path, fname):
    """read a file in repo_dir/file or repo_dir/.git/file"""
    bare = os.path.join(path, fname)
    non_bare = os.path.join(path, ".git", fname)
    if os.path.isfile(bare):
        file_path = bare
    elif os.path.isfile(non_bare):
        file_path = non_bare
    else:
        return None
    with open(file_path, "r") as in_fh:
        return in_fh.read().strip()


def fmt_time(timestamp, fmt="def", offset=None):
    """format a timestamp"""

    if fmt == "def":
        fmt = "%Y-%m-%d %H:%M"
    elif fmt == "iso":
        fmt = "%Y-%m-%dT%H:%M:%SZ"

    elif fmt == "full":
        if offset is not None:
            fmt = "%c %z"
            tzinfo = timezone(timedelta(minutes=offset))
            time = datetime.fromtimestamp(timestamp, tzinfo)
        else:
            fmt = "%c"
            time = datetime.fromtimestamp(timestamp)
        return time.strftime(fmt)

    return datetime.utcfromtimestamp(timestamp).strftime(fmt)


def sorter(entries):
    """order a list of entries by descending date first and then by name
    alphanumerically"""
    return sorted(
        sorted(entries, key=lambda x: x["name"]),
        key=lambda x: x["date"],
        reverse=True,
    )


def write_output(template, outfile, **kwargs):
    """render a template and write an output file"""

    templates = pathlib.Path(__file__).parent / "templates"
    file_loader = FileSystemLoader(templates)
    env = Environment(
        loader=file_loader, autoescape=select_autoescape(["html", "xml"])
    )

    templ = env.get_template(template)
    output = templ.render(**kwargs)

    if isinstance(outfile, (str, bytes, os.PathLike)):
        with open(outfile, "w") as out_fh:
            out_fh.write(output)
    else:
        outfile.write(output)

    os.chmod(outfile, 0o644)


def mkdir(path):
    """make a directory with the right permissions"""
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    os.chmod(path, 0o755)
