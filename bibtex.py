#!/usr/bin/env python
# encoding: utf-8

# Library to convert entries into bibtex entries

TYPES = {
    "journal article": "article",
    "proceedings paper": "inproceedings"
}


def print_key(entry, key):
    if key in entry:
        print "  %s = {{%s}}" % (key, entry[key])


def to_bibtex(entry, crossref, short=True, crossrefs=False):
    print entry
    entryType = TYPES.get(entry["type"].lower(), "misc")

    print "%% [%s] %s" % (entry["citekey"], entry["type"])
    print "@%s{%s," % (entryType, entry["citekey"])

    author_list = " and ".join("%s, %s" % (author["surname"], author["firstname"]) for author in entry.get("authors", []))
    print "  author = {%s}," % author_list

    print_key(entry, "year")
    print_key(entry, "title")
    print_key(entry, "booktitle")

    print "}"
    print
    print entry
