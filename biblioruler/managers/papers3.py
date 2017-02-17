#!/usr/bin/env python
# encoding: utf-8

import sys
import sqlite3
import argparse
import os
import json
import datetime
import logging
import platform

import biblioruler.managers.base as managers


ANNOTATION_QUERY = """SELECT * FROM Annotation WHERE object_id = "{}" """
PDF_QUERY = """SELECT uuid, is_primary, path, md5 FROM PDF WHERE object_id = "{}" """


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
            logging.info("Papers3 database path: " + DEFAULTS["dbpath"])

    return DEFAULTS


# --- Get default db path (on MAC)

# Interface to papers

class Paper(managers.Paper):
    @staticmethod
    def surrogate(papers3, uuid):
        p = Paper(uuid, None)
        p.papers3 = papers3
        return p

    def __getattribute__(self, name):
        # Surrogate
        if name != "uuid" and managers.Paper.__getattribute__(self, "type") is None:
            logging.info("RETRIEVING PAPER FOR %s\n" % name)
            p = self.papers3.get_publication_by_uuid(uuid)
            self.__dict__ = p.__dict__.copy()
        return managers.Paper.__getattribute__(self, name)

    def annotations(self):
        c = self.papers3.dbconn.cursor()
        c2 = self.papers3.dbconn.cursor()
        try:
            c.execute(PDF_QUERY.format(self.uuid))
            for row in c:
                print(row)

                c2.execute(ANNOTATION_QUERY.format(row["uuid"]))
                for row2 in c2:
                    print(row2)
                # self.publications.append(Paper.surrogate(self.papers3, row["object_id"]))
        finally:
            c.close()
            c2.close()

class Author(managers.Author):
    def __init__(self, uuid, firstname, surname):
        managers.Author.__init__(self, uuid, firstname, surname)

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
                c.execute("""SELECT object_id FROM CollectionItem WHERE collection="{}" """.format(self.uuid))
                for row in c:
                    self.publications.append(Paper.surrogate(self.papers3, row["object_id"]))
            finally:
                c.close()
            return self.publications

        return managers.Collection.__getattribute__(self, name)

def dict_factory(cursor, row):
    """Used to extract results from a sqlite3 row by name"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Papers3(managers.Manager):
    """Interface to Papers3.app"""

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

    _xlate_month = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }

    def __init__(self, dbpath=defaults()["dbpath"]):
        """Initialize the papers object"""
        self.dbpath = dbpath
        self.dbconn = sqlite3.connect(dbpath)

        ## Checks to see if this is a valid db connection
        c = self.dbconn.cursor()
        try:
            c.execute("SELECT * FROM metadata LIMIT 1;")
        except sqlite3.OperationalError:
            raise ValueError("Invalid Papers3 database")
        self.dbconn.row_factory = dict_factory

    def parse_publication_date(self, pub_date, translate_month=True, month=(6, 7),
                               year=(2, 5)):
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

    def get_publication_by_uuid(self, ids, results={}, n=100):
        """Get a publication by its universal ID"""
        return self.get_publications("uuid", ids, results, n)

    def get_publication_by_id(self, ids, results={}, n=100):
        """Get a publication by its internal ID"""
        return self.get_publications("rowid", ids, results, n)

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
                   startpage, endpage, citekey, editor_string, abbreviation, type, uuid, summary
                   FROM Publication"""
    def get_publications(self, key, values, results={}, n=100):
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
        paper = Paper(row['uuid'], self.pub_type.get(row["type"], "unknown"))
        paper.papers3 = self

        paper.title = row['attributed_title']

        date = self.parse_publication_date(row['publication_date'])

        if date['month'] is not None:
            paper.month = date['month']
        if date['year'] is not None:
            paper.year = date['year']

        field_mapping = {'number': 'number', 'volume': 'volume', 'editor_string': 'editor', 'abbreviation': 'abbreviation'}
        for field_src, field_dest in field_mapping.items():
            setattr(paper, field_dest, row[field_src])

        # Bundle
        if row["bundle"] != None:
            r = self.get_publication_by_uuid([row["bundle"]])
            if row["bundle"] in r:
                paper.container = r[row["bundle"]]

        paper.abstract = row["summary"]

        # Retrieve authors
        authors = self.dbconn.cursor()
        authors.execute(Papers3.AUTHOR_QUERY % paper.uuid)
        for author in authors:
            paper.authors.append(Author(author['uuid'], author['prename'], author['surname']))
        authors.close()


        return paper


    @staticmethod
    def create(prefix, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--%sdbpath' % prefix, dest="dbpath", default=DEFAULTS['dbpath'],
                            help="The path to the Papers3 sqlite database, "
                            "defaults to [%s]." % DEFAULTS['dbpath'])
        parser.add_argument("--%shelp" % prefix, action="help", help="Provides helps about arguments for this manager")
        args, remaining_args = parser.parse_known_args(args)
        return Papers3(args.dbpath), remaining_args

Manager = Papers3

# # --- Command [get annotations] ---


# def command_get_annotations(app, options):
#     r = app.query_papers_by_citekey([options.citekey])

#     papers = [p for p in r.values()]
#     if len(papers) == 1:
#         papers[0].annotations()


# # --- Command [get] ---


# def command_get(app, options):
#     r = app.query_papers_by_citekey([options.citekey])
#     # Retrieve cross references
#     # for pub in list(r.values()):
#     #     if "bundle" in pub is not None and pub["bundle"] not in r:
#     #         app.get_publication_by_uuid([pub["bundle"]], r)
#     sys.stdout.write(jsonpickle.encode(r))


# # --- Command [get] ---


# # --- Command [get] ---

# def command_bibtex(app, options):
#     r = app.query_papers_by_citekey([options.citekey],)

#     for pub in list(r.values()):
#         sys.stdout.write(bibtex.to_bibtex(pub, crossref))

# # # --- Main part ----


# # if __name__ == '__main__':
# #     defaults()

# #     # create the top-level parser
# #     parser = argparse.ArgumentParser(description='Papers3 utility helper.')
# #     parser.add_argument('-d', '--dbpath', dest="dbpath", default=DEFAULTS['dbpath'],
# #                         help="The path to the Papers3 sqlite database, "
# #                         "defaults to [%s]. If this is set, it will "
# #                         "override the value set in your ~/.papersrc"
# #                         "file." % DEFAULTS['dbpath'])
# #     parser.add_argument('-v', '--verbose', action='store_true', default=False,
# #                         help='Make some noise')

# #     subparsers = parser.add_subparsers(help='sub-command help', dest='command')

# #     # "get" command
# #     parser_get = subparsers.add_parser("get-annotations", help="Retrieves the annotations")
# #     parser_get.add_argument("citekey", help="The cite key")

# #     # "get" command
# #     parser_get = subparsers.add_parser("get", help="Retrieves an entry from Papers3 database given its citekey")
# #     parser_get.add_argument("citekey", help="The cite key")

# #     # "bibtex" command
# #     parser_bibtex = subparsers.add_parser("bibtex", help="Retrieves bibtex entries from Papers3 database given its citekey(s)")
# #     parser_bibtex.add_argument("citekey", help="The cite key")

# #     # "collections" command
# #     parser_collections = subparsers.add_parser("collections", help="Retrieves papers3 collections")

# #     options = parser.parse_args()

# #     try:
# #         app = Papers3(options.dbpath)
# #     except ValueError:
# #         parser.error("Problem connecting to database, is the following "
# #                      "path to your Database.papersdb database correct?\n"
# #                      "\t%s\n" % options.dbpath)
# #     try:
# #         fname = "command_%s" % options.command.replace("-", "_")
# #         locals()[fname](app, options)
# #     except Exception as e:
# #         print("Error while running command %s:" % options.command)
# #         raise
