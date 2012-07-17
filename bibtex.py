#!/usr/bin/env python
# encoding: utf-8

# Library to convert entries into bibtex entries

TYPES = {
    "journal article": "article"
}

def print_key(entry, key):
    if entry.has_key(key):
        print "  %s = {{%s}}" % (key, entry[key])

def to_bibtex(entry):
    print entry
    entryType = TYPES.get(entry["type"].lower(), "misc")
    
    print "%% [%s] %s" % ( entry["citekey"], entry["type"])
    print "@%s{%s," % (entryType, entry["citekey"]) 
    
    author_list = " and ".join("%s, %s" % (author[0], author[1]) for author in entry.get("authors", []))
    print "  author = {%s}," % author_list
    
    print_key(entry, "year")
    print_key(entry, "title")
    print_key(entry, "booktitle")
    
    print "}"
    print
    print entry