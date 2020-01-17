#
# Common classes for bibliography managers
#

import logging
import os.path as op
import os
from bs4 import BeautifulSoup

"""All the types that can be taken by a paper"""
types = set(["article", "article-journal", "article-magazine", "article-newspaper",
    "bill", "book", "broadcast", "chapter", "dataset", "entry", "entry-dictionary",
    "entry-encyclopedia", "figure", "graphic", "interview", "journal", "legal_case", "legislation",
    "manuscript", "map", "motion_picture", "musical_score", "pamphlet", "paper-conference", "proceedings", "patent",
    "personal_communication", "post", "post-weblog", "report", "review", "review-book", "song", "speech",
    "thesis", "treaty", "webpage"])

class Resource:
    def __init__(self, urn):
        self.urn = urn

    def __call__(self, clazz):
        @classmethod
        def urn(cls):
            return self.urn
        
        clazz.urn = urn
        return clazz


class Object:
    def __init__(self, uuid, surrogate=True):
        self.local_uuid = uuid
        self.surrogate = surrogate

    def setdbvalues(self, cursor, row, include=None, exclude=None, transform={}):
        """Used to extract results from a sqlite3 row by name"""
        for idx, col in enumerate(cursor.description):
            name = col[0]
            if (exclude is None or name not in exclude) and (include is None or name not in include):
                dest = transform.get(name, name)
                setattr(self, dest, row[name])

    def __getattr__(self, name):
        # Retrieve the surrogate if need be
        if name == "surrogate": 
            return False

        if self.surrogate:
            logging.debug("Retrieving surrogate %s [access to %s]" % (self.uuid, name))
            self._retrieve()
            self.surrogate = False
            return getattr(self, name)

        raise AttributeError("No attribute %s in %s" % (name, type(self)))

    def _retrieve(self):
        raise Exception("Lazy loading not implemented for %s" % type(self))

    @property
    def uuid(self):
        return "%s:%s" % (self.urn(), self.local_uuid)

    @classmethod
    def urn(cls):
        return None

class Note(Object):
    def __init__(self, uuid, text=None, html=None, title=None, surrogate=True):
        Object.__init__(self, uuid, surrogate=surrogate)
        self._text = text
        self._html = html
        self.title = title
    
    @property
    def html(self):
        return self._html
    
    @property
    def text(self):
        if self._text is None and self._html:
            self._text = BeautifulSoup(self._html).get_text()
        return self._text
    

class Paper(Object):
    """A paper
    
    The following fields are present:
    - authors : a list of authors
    - files : the attached files
    - keywords : the set of keywords
    """
    def __init__(self, uuid, surrogate=True):
        super().__init__(uuid, surrogate)
        self.local_uuid = uuid


    def init(self):
        """Initialize properly the fields"""
        self.authors = []
        self.files = []
        self.keywords = set()
        self.notes = []
        self.container = None
        self.month = None
        self.year = None
        self.read = False
        self.uri = None
        self.doi = None
        self.volume = None
        self.pages = None

        # When the paper was added to the library
        self.creationdate = None

    def __setattr__(self, name, value):
        if name == "type" and value is not None:
            if not value in types:
                raise ValueError("Publication type [%s] is not allowed" % value)

        try:
            object.__setattr__(self, name, value)
        except AttributeError as e:
            logging.error("Cannot set attribute %s on %s" % (name, type(self)))
            raise

    def date(self):
        s = ""
        if self.month is not None:
            s += str(self.month) + " "
        if self.year is not None:
            s += str(self.year) + " "
        return s.strip()



class File(Object):
    """A file (PDF, etc) associated to a document"""
    def __init__(self, uuid: str, surrogate=True):
        """Initialize the File object

        :param uuid: The local UUID
        """
        super().__init__(uuid, surrogate)
        self.title = None
        self.mimetype = None
        self.path = None
        self._annotations = []

    def has_externalannotations(self):
        """Returns False if the file has embedded annotations or has no annotations, True otherwise"""
        return self.annotations
    
    def exists(self):
        if not op.isfile(self.path): 
            return False
        s = os.stat(self.path)
        return s.st_size > 0

    @property
    def annotations(self):
        """Returns the annotations of the file"""
        annotations = self.retrieve_annotations()
        return annotations

    def embed_annotations(self, path):
        import PyPDF2

        inpdf = PyPDF2.PdfFileReader(self.path, 'rb')
        if inpdf.isEncrypted:
            # PyPDF2 seems to think some files are encrypted even
            # if they are not. We just ignore the encryption.
            # This seems to work for the one file where I saw this issue
            inpdf._override_encryption = True
            inpdf._flatten()

        outpdf = PyPDF2.PdfFileWriter()
        pages = []
        for i in range(inpdf.getNumPages()):
            pages.append(inpdf.getPage(i))

        for annotation in self.annotations:
            annotation.annotate(outpdf, pages)
        for page in pages:
            outpdf.addPage(page)

        with open(path, "wb") as file:
            outpdf.write(file)


class Annotation(Object):
    """An annotation on a file"""
    def __init__(self, uuid, file, page, *, surrogate=True, author=None, date=None):
        super().__init__(uuid, surrogate)
        self.file = file
        self.author = author
        self.date = date
        self.page = page

class HighlightAnnotation(Annotation):
    def __init__(self, uuid: str, file: File, page: int, color, 
        date=None, author=None, surrogate=True):
        super().__init__(uuid, file, page, surrogate=surrogate, date=date, author=author)
        self.bboxes = []
        self.color = color

    def addBBox(self, bbox):
        self.bboxes.append(bbox)

    def annotate(self, outpdf, pages):
        import biblioruler.pdf.pdfannotation as pdfannotation
        if len(pages) > self.page:
            annot = pdfannotation.highlight_annotation(self.bboxes, cdate=self.date)
            pdfannotation.add_annotation(outpdf, pages[self.page], annot)
        else:
            logging.warn("Annotated page %d greater than number of pages %d", self.page+1, len(pages))

class NoteAnnotation(Annotation):
    def __init__(self, uuid: str, file: File, page: int, bbox, color, text, 
        surrogate=True, author=None, date=None):
        super().__init__(uuid, file, page, surrogate=surrogate, author=author, date=date)
        self.bbox = bbox
        self.text = text
        self.color = color

    def annotate(self, outpdf, pages):
        import biblioruler.pdf.pdfannotation as pdfannotation
        note = pdfannotation.text_annotation(self.bbox, contents=self.text, author=self.author,
                                                cdate=self.date)
        if len(pages) > self.page:
            pdfannotation.add_annotation(outpdf, pages[self.page], note)
        else:
            logging.warn("Annotated page %d greater than number of pages %d", self.page+1, len(pages))




class Author(Object):
    """The author of a paper"""
    def __init__(self, uuid, firstname=None, surname=None, surrogate=True):
        super().__init__(uuid, surrogate)
        self.firstname = firstname
        self.surname = surname


class Keyword(Object):
    """A keyword"""
    def __init__(self, uuid, name):
        self.parent = None
        self.local_uuid = uuid
        self.name = name


class Collection(Object):
    """A collection of publications"""
    def __init__(self, uuid, name):
        self._parent = None
        self.children = []
        self.publications = []
        self.local_uuid = uuid
        self.name = name
    
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        self._parent.children.append(self)

    def __str__(self):
        if self.parent is None:
            return "%s" % self.name
        return "%s -> %s" % (self.name, self.parent.uuid)


class Manager(Object):
    """A bibliographic manager"""
    pass