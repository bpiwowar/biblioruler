#!/usr/bin/env python
# encoding: utf-8

import sqlite3
import argparse
import bibtex
import os

DEFAULTS = {
    'dbpath': os.path.expanduser("~/Library/Application Support/Papers2/Library.papers2/Database.papersdb"),
}

# Interface to papers


def dict_factory(cursor, row):
    """Used to extract results from a sqlite3 row by name"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Papers(object):
    """Interface to Papers2.app"""

    """Publication type """
    pub_type = {
        -1000: 'book chapter',
        -300: 'website',
        -200: 'conference',
        -100: 'journal',
        300: 'artwork',
        400: 'proceedings paper',
        500: 'patent',
        700: 'technical report',
        0: 'book',
    }

    _xlate_month = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }

    def __init__(self, dbpath):
        """Initialize the papers object"""
        self.dbpath = dbpath
        self.dbconn = sqlite3.connect(dbpath)

        ## Checks to see if this is a valid db connection
        c = self.dbconn.cursor()
        try:
            c.execute("SELECT * FROM metadata LIMIT 1;")
        except sqlite3.OperationalError:
            raise ValueError("Invalid Papers database")
        self.dbconn.row_factory = dict_factory

    def parse_publication_date(self, pub_date, translate_month=True, month=(6, 7),
                               year=(2, 5)):
        """99200406011200000000222000 == Jun 2004
        returns (month, year) as strings
        """
        try:
            cmonth = pub_date[month[0]:month[1] + 1]
            if translate_month:
                cmonth = Papers._xlate_month[cmonth]
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

    def get_publications(self, key, values, results={}, n=100):
        """Returns summary information for each paper matched to papers.

        The returned object is a `dict` keyed on the citekey for each paper,
        the values are dicts with the following minimal paper info:

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
        query = """SELECT rowid as rowid, publication_date, full_author_string,
                   attributed_title, bundle, volume, number,
                   startpage, endpage, citekey, editor_string, abbreviation, type
                   FROM Publication WHERE %s IN (%s)"""
        authorQuery = """SELECT o.surname, o.prename FROM OrderedAuthor oa, Author o
                         WHERE oa.author_id = o.rowid and object_id=%d ORDER BY priority"""
        c = self.dbconn.cursor()
        while len(values) > 0:
            take = min(len(values), n)
            cites = ['"%s"' % x for x in values[0:take]]
            cites = ','.join(cites)
            values = values[take:]
            #print query % (key, cites)
            c.execute(query % (key, cites))
            for row in c:
                date = self.parse_publication_date(row['publication_date'])
                id = row['rowid']
                entry = {
                    'id': id,
                    'title': row['attributed_title'],
                    'citekey': row['citekey'],
                    'authors': []
                }
                if date['month'] is not None:
                    entry['month'] = date['month']
                if date['year'] is not None:
                    entry['year'] = date['year']

                field_mapping = {'number': 'number', 'volume': 'volume', 'editor_string': 'editor',
                                 'bundle': 'bundle', 'abbreviation': 'abbreviation', 'type': 'type'}
                for field_src, field_dest in field_mapping.iteritems():
                    if field_src in row and row[field_src] not in (None, ""):
                        entry[field_dest] = row[field_src]

                if row['startpage'] is not None and row['endpage'] is not None:
                    entry['pages'] = "%s--%s" % (row['startpage'], row['endpage'])

                entry["type"] = self.pub_type.get(entry["type"], "unknown")

                # Retrieve authors
                authors = self.dbconn.cursor()
                authors.execute(authorQuery % id)
                for author in authors:
                    entry["authors"].append({'firstname': author['prename'], 'surname': author['surname']})
                authors.close()

                results[id] = entry
        c.close()
        return results

# --- Command [get] ---


def command_get(app, options):
    r = app.query_papers_by_citekey([options.citekey])
    # Retrieve cross references
    for pub in r.values():
        if pub["bundle"] is not None and pub["bundle"] not in r:
            app.get_publication_by_id([pub["bundle"]], r)
    print r


# --- Command [get] ---

def command_bibtex(app, options):
    r = app.query_papers_by_citekey([options.citekey])

    for pub in r.values():
        crossref = {}
        if pub["bundle"] is not None and pub["bundle"] not in crossref:
            crossref = app.get_publication_by_id([pub["bundle"]], crossref)

        print "[PUB] %s" % pub
        print "[CROSSREF] %s" % crossref
        print bibtex.to_bibtex(pub, crossref)

# --- Main part ----


if __name__ == '__main__':
    # create the top-level parser
    parser = argparse.ArgumentParser(description='Papers2 utility helper.')
    parser.add_argument('-d', '--dbpath', dest="dbpath", default=DEFAULTS['dbpath'],
                        help="The path to the Papers2 sqlite database, "
                        "defaults to [%s]. If this is set, it will "
                        "override the value set in your ~/.papersrc"
                        "file." % DEFAULTS['dbpath'])
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Make some noise')

    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    # "get" command
    parser_get = subparsers.add_parser("get", help="Retrieves an entry from Papers2 database given its citekey")
    parser.add_argument("citekey", help="The cite key")

    # "bibtex" command
    parser_bibtex = subparsers.add_parser("bibtex", help="Retrieves bibtex entries from Papers2 database given its citekey(s)")

    options = parser.parse_args()

    try:
        app = Papers(options.dbpath)
    except ValueError:
        parser.error("Problem connecting to database, is the following "
                     "path to your Database.papersdb database correct?\n"
                     "\t%s\n" % options.dbpath)
    try:
        fname = "command_%s" % options.command.replace("-", "_")
        locals()[fname](app, options)
    except Exception as e:
        print "Error while running command %s:" % options.command
        raise
