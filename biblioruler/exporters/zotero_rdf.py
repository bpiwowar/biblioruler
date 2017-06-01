import xml.sax.saxutils
import argparse
import os.path as op
import os
import io
import re
import logging
import PyPDF2

def escape(string: str):
    """Escape string for XML"""
    if string is None:
        return None
    return xml.sax.saxutils.escape(string)

def write(out: io.IOBase, _indent: int, string: str, *objects, condition=True):
    """Write a line to a stream with a given indent"""
    if condition:
        for _i in range(_indent):
            out.write("  ")
        if objects:
            out.write(string.format(*objects))
        else:
            out.write(string)

# Bibliographic types
BIBTYPE = {
}

# Zotero type mapping from CSL
ZTYPE = {
    "paper-conference": "conferencePaper",
    "article-journal": "journalArticle",
    "report": "report",
    "book": "book",
    "chapter": "bookSection",
    "journal": "journal",
    "patent": "patent",
    "webpage": "webpage",
    "thesis": "thesis",
    "entry": "document",
    "bill": "hearing"
}


RE_FILECHARS = re.compile(r"""[/:\-"']""")


class Exporter:
    def __init__(self):
        """Initalize the exporter
        """
        self.embed_container = True
        self.annotate = False
        self.path = None

    def export(self, path, publications, collections):
        self.path = path

        if self.annotate:
            os.makedirs(path, exist_ok=True)
        with open(path + ".rdf", "wt") as out:
            out.write("""<rdf:RDF
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:z="http://www.zotero.org/namespaces/export#"
         xmlns:dcterms="http://purl.org/dc/terms/"
         xmlns:bib="http://purl.org/net/biblio#"
         xmlns:foaf="http://xmlns.com/foaf/0.1/"
         xmlns:link="http://purl.org/rss/1.0/modules/link/"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:vcard="http://nwalsh.com/rdf/vCard#"
         xmlns:prism="http://prismstandard.org/namespaces/1.2/basic/">\n\n""")

            for p in publications:
                self.output_paper(out, p, indent=1)
                for f in p.files:
                    self.output_file(out, f, indent=2)

            for c in collections:
                self.output_collection(c, out, indent=1)

            out.write("""</rdf:RDF>\n""")

    def output_paper(self, f, paper, indent=0):
        _indent = "  " * indent
        gtype = BIBTYPE.get(paper.type, "Article")

        write(f, indent, '<bib:{} rdf:about="#{}">\n', gtype, paper.uuid)

        if len(paper.authors) > 0:
            write(f, indent+1, u"<bib:authors><rdf:Seq>\n")
            for author in paper.authors:
                write(f, indent+2, "<rdf:li>\n")
                self.output_author(author, f, indent + 3)
                write(f, indent+2, "</rdf:li>\n")
            write(f, indent+1, u"""</rdf:Seq></bib:authors>\n""")

        f.write(u"""%s  <z:itemType>%s</z:itemType>\n""" % (_indent, ZTYPE[paper.type]))
        write(f, indent+1, """<dc:title>{}</dc:title>\n""", escape(paper.title))

        if hasattr(paper, "abstract"):
            write(f, indent+1, """<dcterms:abstract>{}</dcterms:abstract>\n""", escape(paper.abstract), condition=paper.abstract)


        for keyword in paper.keywords:
            write(f, indent+1, """<dc:subject>{}</dc:subject>""", escape(keyword))

        if paper.container is not None:
            if self.embed_container:
                write(f, indent+1, """<dcterms:isPartOf>\n""")
                self.output_paper(f, paper.container, indent+2)
                write(f, indent+1, """</dcterms:isPartOf>\n""")
            else:
                write(f, indent+1, """<dcterms:isPartOf rdf:resource="{}"/>\n""", paper.container.uuid)


        date = paper.date()
        write(f, indent+1, u"""<dc:date>{}</dc:date>\n""", date, condition=len(date) > 0)

        for note in paper.notes:
            write(f, indent+1, """ <dcterms:isReferencedBy rdf:resource="#{}"/>\n""", note.uuid)

        write(f, indent, u"""</bib:{}>\n\n""", gtype)

        for note in paper.notes:
            write(f, indent, """<bib:Memo rdf:about="#{}">""", note.uuid)
            write(f, indent+1, escape(note.html))
            write(f, indent, """</bib:Memo>""")

    def output_author(self, author, f, indent=0):
        _indent = "  " * indent
        write(f, indent, "<foaf:Person>\n")
        write(f, indent+1, "<foaf:surname>{}</foaf:surname>\n", author.surname)
        write(f, indent+1, "<foaf:givenname>{}</foaf:givenname>\n", author.firstname)
        write(f, indent, "</foaf:Person>\n")

    def output_file(self, out, f, indent=0):
        if f.exists():
            """Output a file"""
            write(out, indent, """<z:Attachment rdf:about="#{}">\n""", f.uuid)
            write(out, indent+1, """<z:itemType>attachment</z:itemType>\n""")
            # write(out, indent+1, """<dc:subject>{}</dc:subject>\n""", subject)
            write(out, indent+1, """<dc:title>{}</dc:title>\n""", f.title, condition=f.title)
            write(out, indent+1, """<link:type>{}</link:type>\n""", f.mimetype, condition=f.mimetype)


            if self.annotate and f.has_externalannotations():
                uuidpath = RE_FILECHARS.sub("_", f.uuid)
                path = op.join(self.path, uuidpath + "-" + op.basename(f.path))
                logging.debug("Writing annotated PDF [%s] from [%s]", path, f.path)
                try:
                    f.embed_annotations(path)
                except Exception as e:
                    if op.exists(path): os.remove(path)
                    if isinstance(e, PyPDF2.utils.PdfReadError) or isinstance(e, IOError):
                        logging.error("Error while annotating (%s): %s", type(e), e)
                        write(out, indent+1, """<rdf:resource rdf:resource="{}"/>\n""", f.path)
                    else:
                        raise
                    
            else:
                write(out, indent+1, """<rdf:resource rdf:resource="{}"/>\n""", f.path)
            write(out, indent, """</z:Attachment>\n""")

    def output_collection(self, collection, f, indent=0):
        _indent = "  " * indent
        write(f, indent, """<z:Collection rdf:about="#{}">\n""", collection.uuid)
        write(f, indent + 1, """<dc:title>{}</dc:title>\n""", collection.name)

        for c in collection.children:
            write(f, indent + 1, """<dcterms:hasPart rdf:resource="#{}"/>\n""", c.uuid)

        for p in collection.publications:
            write(f, indent + 1, """<dcterms:hasPart rdf:resource="#{}"/>\n""", p.uuid)

        write(f, indent, "</z:Collection>\n\n")


    @staticmethod
    def create(prefix, args):
        self = Exporter()
        parser = argparse.ArgumentParser(add_help=False)
        def add_argument(name, *args, **kwargs):
            parser.add_argument("--%s%s" % (prefix, name), *args, **kwargs, dest=name)

        add_argument("help", action="help", help="Provides helps about arguments for this manager")
        add_argument("annotate", action="store_true", help="Export files with embedded annotations")

        args, remaining_args = parser.parse_known_args(args, namespace=self)
        return self, remaining_args


