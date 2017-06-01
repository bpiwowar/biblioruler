# Mendeley SQL backend

import biblioruler.managers.base as managers
from dateutil import parser as dtparser
from urllib.parse import unquote
from urllib.parse import urlparse

from .base import Resource, Note, HighlightAnnotation, NoteAnnotation
from biblioruler.sqlite3utils import dict_factory
import argparse
import sqlite3
import os
import os.path as op
import logging
import platform
import datetime as dt

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
            DEFAULTS["dbpath"] = op.join(op.expanduser("~/Library/Application Support/Mendeley Desktop/"),
                plist["MendeleyWeb.userEmail"] + "@www.mendeley.com.sqlite")
            logging.info("Mendeley database path: " + DEFAULTS["dbpath"])

    return DEFAULTS

@Resource(urn="mendeley:paper")
class Paper(managers.Paper):
    """A Mendeley paper"""
    BASE_QUERY = """SELECT d.uuid as __uuid, d.type as __type, d.id, d.userType as __userType, 
                d.publication as __publication, d.note as __note, d.added as __added,
                d.title, d.issn, d.isbn, d.year, d.month, d.pages, d.pmid, d.doi,
                d.read, d.favourite, d.abstract, d.institution
                FROM Documents d"""

    AUTHORS_QUERY = """SELECT contribution, firstNames, lastName FROM DocumentContributors WHERE documentId=%d ORDER BY id"""
    TAG_QUERY = """SELECT tag FROM DocumentTags WHERE documentId=%d"""
    FILE_QUERY = """SELECT df.hash, f.localUrl FROM DocumentFiles df, Files f WHERE df.hash=f.hash AND documentId=%d"""

    TYPES = {
        'Book': 'book',
        'WorkingPaper': 'report',
        'report': 'report',
        'ConferenceProceedings': 'paper-conference',
        'Thesis': 'thesis', # phd or master -> userType
        'MagazineArticle': 'article-journal',
        'Patent': 'patent',
        'WebPage': 'webpage',
        'Generic': 'entry',
        'JournalArticle': 'article-journal',
        'BookSection': 'chapter',
        'Report': 'report',
        'Bill': 'bill'
    }

    def __init__(self, manager, uuid):
        managers.Paper.__init__(self, uuid)
        self.manager = manager

    def populate(self, row):
        self.init()

        """Populate from DB"""
        for key, value in row.items():
            if not key.startswith("__"):
                setattr(self, key, value)

        self.type = Paper.TYPES[row["__type"]]

        if self.type in ["article-journal", "paper-conference"] and row["__publication"]:
            self.container = Paper(self.manager, "container:%s" % self.local_uuid)
            self.container.init()
            self.container.title = row["__publication"]
            self.container.type = "journal"
            self.container.surrogate = False

        if row["__note"] is not None:
            self.notes.append(Note(html=row["__note"], uuid="paper:%d:note" % (self.id)))

        if row["__added"] is not None:
            self.creationdate = dt.datetime.fromtimestamp(row["__added"] / 1000)

        c = self.manager.dbconn.cursor()
        try:
            c.execute(Paper.AUTHORS_QUERY % self.id)
            for ix, row in enumerate(c):
                self.authors.append(Author(firstname=row["firstNames"], surname=row["lastName"], uuid="paper:%d:author:%d" % (self.id, ix), surrogate=False))
        finally:
            c.close()

        c = self.manager.dbconn.cursor()
        try:
            c.execute(Paper.TAG_QUERY % self.id)
            for ix, row in enumerate(c):
                self.keywords.add(row["tag"])
        finally:
            c.close()

        # Get tags
        c = self.manager.dbconn.cursor()
        try:
            c.execute(Paper.TAG_QUERY % self.id)
            for ix, row in enumerate(c):
                self.keywords.add(row["tag"])
        finally:
            c.close()

        # Get files
        c = self.manager.dbconn.cursor()
        try:
            c.execute(Paper.FILE_QUERY % self.id)
            for ix, row in enumerate(c):
                self.files.append(File(self.manager, row["hash"], row["localUrl"]))
        finally:
            c.close()
            

        self.surrogate = False

    @staticmethod
    def createFromDB(manager, row):
        paper = Paper(manager, "%s" % row["__uuid"])
        paper.populate(row)
        return paper



def converturl2abspath(url):
    """Convert a url string to an absolute path"""
    pth = unquote(str(urlparse(url).path))
    return os.path.abspath(pth)

@Resource(urn="mendeley:file")
class File(managers.File):
    """A file"""
    def __init__(self, manager, uuid, localUrl):
        managers.File.__init__(self, uuid, surrogate=False)
        self.manager = manager
        self.path = converturl2abspath(localUrl)

    def retrieve_annotations(self):

        query = """SELECT fhr.id, fhr.page, fhr.highlightId,
                                fhr.x1, fhr.y1,
                                fhr.x2, fhr.y2,
                                fh.createdTime,
                                color
                        FROM FileHighlights fh
                        LEFT JOIN FileHighlightRects fhr
                            ON fhr.highlightId=fh.id
                        WHERE (fhr.page IS NOT NULL) AND fh.fileHash=:hash
                        ORDER BY fhr.highlightId"""
        annotations = []

        annotation = None
        highlightId = None

        ret = self.manager.dbconn.execute(query, { "hash": self.local_uuid })
        for r in ret:
            page = r["page"] - 1
            bbox = [r["x1"], r["y1"], r["x2"], r["y2"]]
            cdate = dtparser.parse(r["createdTime"])
            uuid = "%s:note:%s" % (self.uuid, r["id"])
            if annotation is None or annotationId != r["highlightId"]:                   
                annotation = HighlightAnnotation(uuid, self, page, r["color"], date=cdate)
                annotations.append(annotation)
                annotationId = r["highlightId"]

            annotation.addBBox(bbox)

        query = """
            SELECT id, color, FileNotes.page,
                FileNotes.x, FileNotes.y,
                FileNotes.author, FileNotes.note,
                FileNotes.modifiedTime
            FROM FileNotes
            WHERE FileNotes.page IS NOT NULL AND fileHash=:hash""" 
        ret = self.manager.dbconn.execute(query, { "hash": self.local_uuid })

        for r in ret:
            page = r["page"] - 1
            bbox = [r["x"], r["y"], r["x"]+30, r["y"]+30]
            author = r["author"]
            txt = r["note"]
            cdate = dtparser.parse(r["modifiedTime"])
            uuid = "%s:note:%s" % (self.uuid, r["id"])
            NoteAnnotation(uuid, self, page, bbox, r["color"], txt, date=cdate, author=author)

        return annotations

@Resource(urn="mendeley")
class Note(managers.Note):
    """An author"""
    pass

@Resource(urn="mendeley")
class Author(managers.Author):
    """An author"""
    pass





@Resource(urn="mendeley")
class Collection(managers.Collection):
    """A collection"""
    BASE_QUERY = """SELECT f.id, f.name, f.parentId FROM Folders f"""
    DOCUMENT_QUERY = """SELECT d.uuid, documentId, folderId FROM DocumentFolders df, Documents d WHERE d.id = df.documentId"""

    def __init__(self, manager, uuid, name):
        managers.Collection.__init__(self, uuid, name)
        self.manager = manager

    def populate(self, row):
        self.parentId = row["parentId"]
        self.id = row["id"]

        c = self.manager.dbconn.cursor()
        try:
            c.execute(Collection.DOCUMENT_QUERY + " AND folderId=%d" % self.id)
            for row in c:
                self.publications.append(Paper(self.manager, "%s" % row["uuid"]))
        finally:
            c.close()

        
        if self.parentId < 0: self.parentId = None


    @staticmethod
    def createFromDB(manager, row):
        collection = Collection(manager, "folder:%s" %  row["id"], row["name"])
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
            query = Collection.BASE_QUERY
            query += """, Groups g, RemoteFolders rf 
                WHERE g.groupType == 'PersonalGroupType' AND rf.folderId = f.id and rf.groupId=g.id"""
            c.execute(query)
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
            query = Paper.BASE_QUERY + """, Groups g, RemoteDocuments rd 
                WHERE g.groupType == 'PersonalGroupType' AND rd.documentId = d.id and rd.groupId=g.id"""
            c.execute(query)
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

