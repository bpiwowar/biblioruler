#!/usr/bin/env python
# encoding: utf-8

import re
import sys
import sqlite3
import argparse
import os.path as op
import os
import json
import datetime
import logging
import platform

import biblioruler.managers.base as managers
from biblioruler.sqlite3utils import dict_factory


ANNOTATION_QUERY = """SELECT uuid, contents, type, text, created_at, left, height, rectangles FROM Annotation WHERE object_id = "{}" """
PDF_QUERY = """SELECT uuid as local_uuid, is_primary, mime_type as mimetype, path, md5 FROM PDF WHERE object_id = "{}" """


DEFAULTS = None
def defaults():
    global DEFAULTS
    if DEFAULTS is not None:
        return DEFAULTS

    DEFAULTS = { "dbpath": None }

    if platform.system() == "Darwin":
        import plistlib

        with open(os.path.expanduser("~/Library/Preferences/com.mekentosj.papers3.plist"), "rb") as fh:
            plist = plistlib.load(fh)
            DEFAULTS["dbpath"] = os.path.expanduser("~/Library/Application Support/") + \
                plist["mt_papers3_library_location_local"] + "/Library.papers3/Database.papersdb"
            DEFAULTS["filebase"] = plist["mt_papers3_full_library_location_shared"]
            logging.info("Papers3 database path: " + DEFAULTS["dbpath"])

    return DEFAULTS


_xlate_month = {
    '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
    '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
    '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
}
def parse_date(pub_date, translate_month=True, month=(6, 7), year=(2, 5)):
    """99200406011200000000222000 == Jun 2004
    returns (month, year) as strings
    """
    try:
        cmonth = pub_date[month[0]:month[1] + 1]
        if translate_month:
            cmonth = Papers3._xlate_month[cmonth]
    except:
        cmonth = ''
    try:
        cyear = pub_date[year[0]:year[1] + 1]
    except:
        cyear = ''

    return {'month': cmonth, 'year': cyear}


# Interface to papers

class Annotation(managers.Annotation):
    def __init__(self, file, uuid):
        super().__init__(file, uuid)


class File(managers.File):
    def __init__(self, paper, uuid):
        super().__init__(uuid)
        self.paper = paper

    def populate(self, cursor, row):
        """
        :param cursor: the db cursor
        :param row: an associative array containing everything
        """
        self.setdbvalues(cursor, row)
        self.path = op.join(self.paper.papers3.filebase, self.path) if self.path is not None else None
        self.surrogate = False

        if self.mimetype == "application/vnd.mekentosj.papers3.html":
            self.mimetype = "application/html"
        return self


    def annotations(self):
        c = self.papers3.dbconn.cursor()
        try:
            c2.execute(ANNOTATION_QUERY.format(row["uuid"]))
            for row2 in c2:
                yield Annotation(row2)
        finally:
            c.close()
            c2.close()

    @classmethod
    def urn(cls):
        return "papers3"

class Paper(managers.Paper):
    """Publication type """
    pub_type = {
        -1000: 'chapter',
        -999: 'entry',
        -300: 'webpage',
        -200: 'proceedings',
        -100: 'journal',
        0: 'book',
        300: 'report', #'artwork',
        400: 'paper-conference',
        500: 'patent',
        700: 'report',
        999: 'entry',
    }

    field_mapping = {'number': 'number', 'volume': 'volume', 'editor_string': 'editor', 'abbreviation': 'abbreviation'}

    def __init__(self, papers3, uuid):
        super().__init__(uuid, True)
        self.papers3 = papers3

    def populate(self, row):
        self.init()
        self.type = Paper.pub_type.get(row["type"], "unknown")
        self.title = row['attributed_title']
        self.doi = row['doi']
        if self.doi:
            self.uri = "papers3://publication/doi/%s" % self.doi
        else:
            self.uri = "papers3://publication/uuid/%s" % self.local_uuid


        date = parse_date(row['publication_date'])

        if date['month'] is not None:
            self.month = date['month']
        if date['year'] is not None:
            self.year = date['year']

        for field_src, field_dest in Paper.field_mapping.items():
            setattr(self, field_dest, row[field_src])

        # Bundle
        if row["bundle"] != None:
            self.container = Paper(self.papers3, row["bundle"])

        self.abstract = row["summary"]

        # Retrieve authors
        authors = self.papers3.dbconn.cursor()
        authors.execute(Papers3.AUTHOR_QUERY % self.uuid)
        for author in authors:
            self.authors.append(Author(author['uuid'], author['prename'], author['surname']))
        authors.close()

        self.surrogate = False

    @staticmethod
    def surrogate(papers3, uuid):
        p = Paper(uuid, None)
        p.papers3 = papers3
        return p


    def files(self):
        c = self.papers3.dbconn.cursor()
        try:
            c.execute(PDF_QUERY.format(self.local_uuid))
            if c.rowcount == 0: return []

            for row in c:
                file = File(self, row["local_uuid"])
                file.populate(c, row)
                yield file
        finally:
            c.close()

    # def _retrieve(self):
    #     p = self.papers3.get_publication_by_uuid(uuid)

    @classmethod
    def urn(cls):
        return "papers3"


class Author(managers.Author):
    def __init__(self, uuid, firstname, surname):
        managers.Author.__init__(self, uuid, firstname, surname)

    @classmethod
    def urn(cls):
        return "papers3"

class Collection(managers.Collection):
    def __init__(self, papers3, *args):
        self.papers3 = papers3
        managers.Collection.__init__(self, *args)
        del(self.publications)

    def __getattr__(self, name):
        if name == "publications":
            c = self.papers3.dbconn.cursor()
            try:
                self.publications = []
                c.execute("""SELECT object_id FROM CollectionItem WHERE collection="{}" """.format(self.local_uuid))
                for row in c:
                    self.publications.append(Paper.surrogate(self.papers3, row["object_id"]))
            finally:
                c.close()
            return self.publications

        return managers.Collection.__getattribute__(self, name)

    @classmethod
    def urn(cls):
        return "papers3"

class Papers3(managers.Manager):
    """Interface to Papers3.app"""

    def __init__(self, dbpath=defaults()["dbpath"], filebase=defaults()["filebase"]):
        """Initialize the papers object"""
        self.dbpath = dbpath
        self.dbconn = sqlite3.connect(dbpath)
        self.filebase = filebase

        ## Checks to see if this is a valid db connection
        c = self.dbconn.cursor()
        try:
            c.execute("SELECT * FROM metadata LIMIT 1;")
        except sqlite3.OperationalError:
            raise ValueError("Invalid Papers3 database")
        self.dbconn.row_factory = dict_factory
        logging.info("Connected to Papers3 SQL database")

    def get_publication_by_uuid(self, ids, results=None, n=100):
        """Get a publication by its universal ID"""
        return self.get_publications("uuid", ids, results, n)

    def get_publication_by_id(self, ids, results=None, n=100):
        """Get a publication by its internal ID"""
        return self.get_publications("rowid", ids, results, n)

    def get_publication_by_doi(self, ids, results=None, n=100):
        """Get a publication by its internal ID"""
        return self.get_publications("doi", ids, results, n)

    def get_publication_by_uri(self, uris, results=None):
        """Get a publication by its papers URI"""
        if not results:
            results = {}
        re_papers_uri = re.compile("papers[23]://publication/(doi|uuid|livfe)/(.*)")
        for uri in uris:
            m = re_papers_uri.match(uri)
            if m is None:
                logging.warn("%s is not a Papers3 URI", uri)
            else:
                uritype = m.group(1)
                uriref = m.group(2)
                logging.debug("Searching for Papers3 publication with key of type %s and value %s", uritype, uriref)
                if uritype in ("uuid", "doi"):
                    r = self.get_publications(uritype, [uriref])
                    if r:
                        results[uri] = list(r.values())[0]
                elif uritype == "doi":
                    pass
                elif uritype == "livfe":
                    pass
                else:
                    assert False, "URI type %s not handled" % uritype # Should never happen
        return results

    def query_papers_by_citekey(self, citekeys, results={}, n=100):
        return self.get_publications("citekey", citekeys, results, n)


    def collections(self, virtual=False):
        """
        Get all the collections
        """

        query = """SELECT uuid, name, collection_description, created_at, parent, priority FROM Collection WHERE %s""" % (
            "true" if virtual else "editable=1")
        c = self.dbconn.cursor()
        try:
            c.execute(query)
            collections = {}
            for row in c:
                collection = Collection(self, row["uuid"], row["name"])
                collection.description = row["collection_description"]
                collection.parent = row["parent"]
                collections[collection.uuid] = collection

            for collection in collections.values():
                if collection.parent is not None:
                    if collection.parent in collections:
                        collection.parent = collections[collection.parent]
                        collection.parent.children.append(collection)

            return collections

        finally:
            c.close()


    PUBLICATION_QUERY = """SELECT publication_date, attributed_title, bundle, volume, number,
                   startpage, endpage, citekey, editor_string, doi, abbreviation, type, uuid, summary
                   FROM Publication"""
    def get_publications(self, key, values, results=None, n=100):
        """Returns summary information for each paper matched to papers.

        The returned object is a `dict` keyed on the citekey for each paper,
        where field names are taken from the CSL terminology.

          - title   : The title of the publicatio
          - authors : Firstname Lastname, First Last, and First Last
          - journal : Journal name (as listed in Publications db)
          - citekey : The citekey

          And optionally, if these are found in the Publication record:

          - volume  : Journal volume
          - number  : Journal number
          - pages   : start--end pages
          - month   : Month of publication date (as 3 letter name)
          - year    : 4 digit (character) year of publication
        """
        query = """%s WHERE %%s IN (%%s)""" % Papers3.PUBLICATION_QUERY
        c = self.dbconn.cursor()
        if not results:
            results = {}
        while len(values) > 0:
            take = min(len(values), n)
            cites = ['"%s"' % x for x in values[0:take]]
            cites = ','.join(cites)
            values = values[take:]
            logging.debug(query % (key, cites))
            c.execute(query % (key, cites))
            for row in c:
                paper = self.get_paper(row)
                results[paper.uuid] = paper
            c.close()
        return results

    def publications(self):
        """Returns all papers"""
        c = self.dbconn.cursor()
        try:
            c.execute(Papers3.PUBLICATION_QUERY)
            for row in c:
                yield self.get_paper(row)
        finally:
            c.close()

    AUTHOR_QUERY = """SELECT o.surname, o.prename, o.uuid FROM OrderedAuthor oa, Author o
                     WHERE oa.author_id = o.uuid and object_id="%s" ORDER BY priority"""

    def get_paper(self, row):
        paper = Paper(self, row['uuid'])
        paper.populate(row)
        return paper


    @staticmethod
    def create(prefix, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--%sdbpath' % prefix, dest="dbpath", default=DEFAULTS['dbpath'],
                            help="The path to the Papers3 sqlite database, "
                            "defaults to [%s]." % DEFAULTS['dbpath'])
        parser.add_argument('--%sfilebase' % prefix, dest="filebase", default=DEFAULTS['filebase'],
                            help="The base path to the Papers3 file location, "
                            "defaults to [%s]." % DEFAULTS['filebase'])
        parser.add_argument("--%shelp" % prefix, action="help", help="Provides helps about arguments for this manager")
        args, remaining_args = parser.parse_known_args(args)
        return Papers3(args.dbpath, args.filebase), remaining_args

Manager = Papers3

