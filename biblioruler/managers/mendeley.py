# Mendeley SQL backend

import biblioruler.managers.base as managers
from biblioruler.sqlite3utils import dict_factory
import argparse
import sqlite3
import os
import logging
import platform

DEFAULTS = None

def defaults():
    """Get defaults"""
    global DEFAULTS
    if DEFAULTS is not None:
        return DEFAULTS

    DEFAULTS = { "dbpath": None, "filebase": None }

    if platform.system() == "Darwin":
        import plistlib

        with open(os.path.expanduser("~/Library/Preferences/com.mendeley.Mendeley Desktop.plist"), "rb") as fh:
            plist = plistlib.load(fh)
            DEFAULTS["dbpath"] = os.path.expanduser("~/Library/Application Support/Mendeley Desktop/") + plist["MendeleyWeb.userEmail"] + "@www.mendeley.com.sqlite"
            logging.info("Mendeley database path: " + DEFAULTS["dbpath"])

    return DEFAULTS

class Paper(managers.Paper):
    """A Mendeley paper"""
    BASE_QUERY = """SELECT uuid, type, id, title, userType, issn, isbn, year, month, pages, pmid,
                read, favourite, note, abstract
                FROM Documents"""
    TYPES = {
        'Book': 'book',
        'WorkingPaper': 'report',
        'report': 'report',
        'ConferenceProceedings': 'proceedings',
        'Thesis': 'thesis', # phd or master -> userType
        'MagazineArticle': 'article-journal',
        'Patent': 'patent',
        'WebPage': 'webpage',
        'Generic': 'entry',
        'JournalArticle': 'article-journal',
    }

    def __init__(self, manager, uuid):
        managers.Paper.__init__(self, uuid)
        self.manager = manager
    
    def populate(self, row):
        self.title = row["title"]
        self.type = Paper.TYPES[row["type"]]
        self.abstract = row["abstract"]

        self.month = row["month"]
        self.year = str(row["year"])
        self.surrogate = False

    @staticmethod
    def createFromDB(manager, row):
        paper = Paper(manager, row["uuid"])
        paper.populate(row)
        return paper

class Author(managers.Author):
    """An author"""
    pass

class Collection(managers.Collection):
    """A collection"""
    BASE_QUERY = """SELECT id, uuid, name, parentId FROM Folders"""

    def __init__(self, manager, uuid, name):
        managers.Collection.__init__(self, uuid, name)
        self.manager = manager

    def populate(self, row):
        self.parentId = row["parentId"]
        self.id = row["id"]
        if self.parentId < 0: self.parentId = None

    @staticmethod
    def createFromDB(manager, row):
        collection = Collection(manager, row["uuid"], row["name"])
        collection.populate(row)
        return collection

class Manager(managers.Manager):
    """Mendeley manager"""
    def __init__(self, dbpath=defaults()["dbpath"], filebase=defaults()["filebase"]):
        """Initialize the manager"""
        managers.Manager.__init__(self, None, surrogate=False)
        self.dbpath = dbpath
        self.dbconn = sqlite3.connect(dbpath)
        self.filebase = filebase

        ## Checks to see if this is a valid db connection
        c = self.dbconn.cursor()
        try:
            c.execute("SELECT * FROM DocumentZotero LIMIT 1;")
        except sqlite3.OperationalError:
            raise ValueError("Invalid Papers3 database")
        self.dbconn.row_factory = dict_factory
    
    def collections(self):
        c = self.dbconn.cursor()
        try:
            collections = {}
            c.execute(Collection.BASE_QUERY)
            for row in c:
                collection = Collection.createFromDB(self, row)
                collections[collection.id] = collection
            
            for collection in collections.values():
                if collection.parentId is not None:
                    collection.parent = collections[collection.parentId]
            return collections
        finally:
            c.close()
        
    def publications(self):
        c = self.dbconn.cursor()
        try:
            c.execute(Paper.BASE_QUERY)
            for row in c:
                yield Paper.createFromDB(self, row)
        finally:
            c.close()


    @staticmethod
    def create(prefix, args):
        """Creates a new manager"""
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--%sdbpath' % prefix, dest="dbpath", default=DEFAULTS['dbpath'],
                            help="The path to the Papers3 sqlite database, "
                            "defaults to [%s]." % DEFAULTS['dbpath'])
        parser.add_argument("--%shelp" % prefix, action="help",
            help="Provides helps about arguments for this manager")
        args, remaining_args = parser.parse_known_args(args)
        return Manager(args.dbpath), remaining_args
