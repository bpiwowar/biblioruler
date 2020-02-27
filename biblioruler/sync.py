# Synchronize command

import logging


def getClass(name):
    source = __import__("manager_%s" % name)
    return source.__dict__[name[0].upper() + name[1:]]


def execute(args):
    source = getClass(args.source)()
    destination = getClass(args.destination)()

    p = source.get_publication_by_uuid(["967C1DCB-DC3B-4334-9F7A-A776A4B40D2C"])
