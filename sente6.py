#!/usr/bin/env python
# encoding: utf-8

import sqlite3
import argparse
import os
import bibtex

DEFAULTS = {
  'dbpath' : os.path.expanduser("~//Documents/Papers/Sente 6 Library.sente6lib/Contents/primaryLibrary.sente601")
}

role_mapping = {
    'Author': 'authors',
    'Editor': 'editors'
}

field_mapping = { 
    'publicationType': 'type', 
    'articleTitle': 'title', 
    'publicationTitle': 'booktitle',
    'ReferenceUUID': 'uuid',
    'issue': 'issue',
    'volume': 'volume',
    'publicationMonth': 'month',
    'publicationYear': 'year',
    'abstractText': 'abstract',
    '_BibTeX cite tag': 'citekey',
    '_custom3': 'uri'
}

# Interface to papers
def dict_factory(cursor, row):
    """Used to extract results from a sqlite3 row by name"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
    
    
def sente_collate(s1,s2):
    return cmp(s1,s2)

class Sente(object):
    """Interface to Sente.app"""

    def __init__(self, dbpath):
        """Initialize the papers object"""
        self.dbpath = dbpath
        self.dbconn = sqlite3.connect(dbpath)

        # Create SenteLocalizedNoCase collation
        self.dbconn.create_collation("SenteLocalizedNoCase", sente_collate)
        
        ## Checks to see if this is a valid db connection
        c = self.dbconn.cursor()        
        try:
            c.execute("SELECT * FROM Reference LIMIT 1;")
        except sqlite3.OperationalError:
            raise ValueError("Invalid Papers database")
        self.dbconn.row_factory = dict_factory
    

    def get_publication_by_uuid(self, ids, results= {}, n = 100):
        """Get a publication by its universal ID"""
        return self.get_publications("uuid", ids, results, n)
    
    def query_papers_by_citekey(self, citekeys, results = {}, n=100):
        return self.get_publications("s.AttributeValue", citekeys, results, n, "JOIN SparseAttribute s ON s.ReferenceUUID=r.ReferenceUUID")
        
        
    def get_publications(self, key, values, results = {}, n=100, join = ""):
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
        query = """SELECT r.*
                   FROM Reference r 
                   %s
                   WHERE %s IN (%s)"""
        c = self.dbconn.cursor()
        while len(values) > 0:
            take = min(len(values), n)
            cites = ['"%s"' % x for x in values[0:take]]
            cites = ','.join(cites)
            values = values[take:]
            c.execute(query % (join, key, cites))
            for row in c:
                id = row['ReferenceUUID']
                
                # Retrieve other fields
                c2 = self.dbconn.cursor()
                c2.execute("SELECT AttributeName as name, AttributeValue as value FROM SparseAttribute WHERE ReferenceUUID like '%s'" % id)
                for row2 in c2:
                    if not row2["value"] is "":
                        row["_%s" % row2["name"]] = row2["value"]
                
                for k,v in row.items(): print("[%s] %s" % (k,v))
                
                entry = {}
                for field_src, field_dest in field_mapping.items():
                    if field_src in row and row[field_src] not in (None, ""): 
                        entry[field_dest] = row[field_src]
                        
                # Retrieve authors
                c2.execute("SELECT LastName, ForeNames, Role FROM Author WHERE ReferenceUUID like '%s' ORDER BY SequenceNumber" % id)
                for row2 in c2:
                    role=row2["Role"]
                    destRole = role_mapping.get(role, None)
                    if destRole is not None:
                        if destRole not in entry: entry[destRole] = []
                        entry[destRole].append([row2["LastName"], row2["ForeNames"]])
                    else: 
                        raise Exception("Unknown role [%s]" % role)
                c2.close()

                    
                results[id] = entry
        c.close()
        return results
        
# --- Command [get] ---
def command_get(app, options):
    entries = app.query_papers_by_citekey([options.citekey])
    for entry in list(entries.values()): bibtex.to_bibtex(entry)
    
# --- Main part ----


if __name__ == '__main__':
    # create the top-level parser
    parser = argparse.ArgumentParser(description='Sente 6 utility helper.')
    parser.add_argument('-d', '--dbpath', dest="dbpath", default= DEFAULTS['dbpath'],
                    help="The path to the Papers2 sqlite database, "  \
                         "defaults to [%s]. If this is set, it will " \
                         "override the value set in your ~/.papersrc" \
                         "file." % DEFAULTS['dbpath'])
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='Make some noise')
    
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
                    
    # "get" command
    parser_get  = subparsers.add_parser("get", help="Retrieves an entry from Papers2 database given its citekey")
    parser_get.set_defaults(func=command_get)
    parser.add_argument("citekey", help="The cite key")
    
    options = parser.parse_args()
        
    try:
        app = Sente(options.dbpath)
    except ValueError:
        parser.error("Problem connecting to database, is the following " \
                     "path to your Database.papersdb database correct?\n" \
                     "\t%s\n" % options.dbpath)
    try: 
        options.func(app, options)
    except Exception as e:
        print("Error while running command %s:" % options.command)
        raise
    


