# pystagit

A static git page generator, heavily inspired by [stagit](https://codemadness.org/git/stagit/file/README.html), but written in Python.

## Usage

pystagit's usage is pretty much copied from stagit

Make files per repository:

```sh
mkdir -p htmldir && cd htmldir
pystagit path-to-repo
```

Make index file for repositories

```sh
pystagit-index repodir1 repodir2 repodir3 > index.html
```

## Build and install

```sh
pip install .
```

## Motivation

Stagit is great. However, I wanted some unnecessary but nice features like
syntax highlighting and markdown rendering. I also didn't like stagit's abuse
of tables to define page layouts.

I considered forking stagit and adding these things to it, but the best syntax
highlighter that I know is [pygments](https://pygments.org/), and calling
an external script from stagit's C code just to use pygments felt too hacky.
So I re-wrote the whole thing in Python.

Being able to use Jinja2 as a template system for the pages was a nice bonus
too.

## Main differences with stagit

* pystagit is much more bloated and slow.
* Source code gets syntax highlight.
* Markdown files get automatically rendered in HTML.
* Less abuse of tables for the page layout (I try to use tables for the data
that is intrinsically tabular).
* Raw plain text files are also generated and easily accessible.

## TODO

* Write tests.
* Improve argument handling.
* Use a cache like stagit does.
