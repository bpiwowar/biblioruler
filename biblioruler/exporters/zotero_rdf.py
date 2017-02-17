import xml.sax.saxutils
import argparse
import os.path as op
import os

def escape(s):
    if s is None:
        return None
    return xml.sax.saxutils.escape(s)

def write(f, _indent, string, *objects, condition=True):
    if condition:
        for i in range(_indent):
            f.write("  ")
        f.write(string.format(*objects))

bibtype = { }
types = set(["article", "article-journal", "article-magazine", "article-newspaper",
    "bill", "book", "broadcast", "chapter", "dataset", "entry", "entry-dictionary",
    "entry-encyclopedia", "figure", "graphic", "interview", "journal", "legal_case", "legislation",
    "manuscript", "map", "motion_picture", "musical_score", "pamphlet", "paper-conference", "proceedings", "patent",
    "personal_communication", "post", "post-weblog", "report", "review", "review-book", "song", "speech",
    "thesis", "treaty", "webpage"])


def output_paper(self, f, indent=0):
    _indent = "  " * indent
    gtype = bibtype.get(self.type, "Article")

    write(f, indent, '<bib:{} rdf:about="#{}">\n', gtype, self.uuid)

    if len(self.authors) > 0:
        write(f, indent+1, u"<bib:authors><rdf:Seq>\n")
        for author in self.authors:
            write(f, indent+2, "<rdf:li>\n")
            output_author(author, f, indent + 3)
            write(f, indent+2, "</rdf:li>\n")
        write(f, indent+1, u"""</rdf:Seq></bib:authors>\n""")

    f.write(u"""%s  <z:itemType>%s</z:itemType>\n""" % (_indent, self.type))
    write(f, indent+1, """<dc:title>{}</dc:title>\n""", escape(self.title))
    write(f, indent+1, """<dcterms:abstract>{}</dcterms:abstract>\n""", escape(self.abstract), condition=self.abstract)

    f.write(u"""%s  <dc:date>%s</dc:date>\n""" % (_indent, self.date()))
    f.write(u"""%s</bib:%s>\n\n""" % (_indent, gtype))

def output_author(self, f, indent=0):
    _indent = "  " * indent
    write(f, indent, "<foaf:Person>\n")
    write(f, indent+1, "<foaf:surname>{}</foaf:surname>\n", self.surname)
    write(f, indent+1, "<foaf:givenname>{}</foaf:givenname>\n", self.firstname)
    write(f, indent, "</foaf:Person>\n")

def output_file(self, f):
    write(f, indent, """<z:Attachment rdf:about="#{}">""", paper)
    write(f, indent+1, """<z:itemType>attachment</z:itemType>""")
    write(f, indent+1, """<rdf:resource rdf:resource="{}"/>""", path)
    write(f, indent+1, """<dc:subject>{}</dc:subject>""", subject)
    write(f, indent+1, """<dc:title>{}</dc:title>""", title)
    write(f, indent+1, """<link:type>{}</link:type>""", mimetype)
    write(f, indent, """</z:Attachment>""")

def output_collection(self, f, indent=0):
    _indent = "  " * indent
    write(f, indent, """<z:Collection rdf:about="#{}">\n""", self.uuid)
    write(f, indent + 1, """<dc:title>{}</dc:title>\n""", self.name)

    for c in self.children:
        write(f, indent + 1, """<dcterms:hasPart rdf:resource="#{}"/>\n""", c.uuid)

    for p in self.publications:
        write(f, indent + 1, """<dcterms:hasPart rdf:resource="#{}"/>\n""", p.uuid)

    write(f, indent, "</z:Collection>\n\n")


class Exporter:
    def export(self, path, publications, collections):
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
                output_paper(p, out, indent=1)

            for c in collections:
                output_collection(c, out, indent=1)

            out.write("""</rdf:RDF>\n""")

    @staticmethod
    def create(prefix, args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--%shelp" % prefix, action="help", help="Provides helps about arguments for this manager")
        args, remaining_args = parser.parse_known_args(args)
        return Exporter(), remaining_args


