#
# Common classes for bibliography managers
#

import logging

"""All the types that can be taken by a paper"""
types = set(["article", "article-journal", "article-magazine", "article-newspaper",
    "bill", "book", "broadcast", "chapter", "dataset", "entry", "entry-dictionary",
    "entry-encyclopedia", "figure", "graphic", "interview", "journal", "legal_case", "legislation",
    "manuscript", "map", "motion_picture", "musical_score", "pamphlet", "paper-conference", "proceedings", "patent",
    "personal_communication", "post", "post-weblog", "report", "review", "review-book", "song", "speech",
    "thesis", "treaty", "webpage"])


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
            logging.debug("Retrieving surrogate %s [access to %s]\n" % (self.uuid, name))
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


class Paper(Object):
    """A paper"""
    def __init__(self, uuid, surrogate=True):
        super().__init__(uuid, surrogate)
        self.local_uuid = uuid
        self.authors = []
        self.keywords = set()
        self.container = None

    def __setattr__(self, name, value):
        if name == "type" and value is not None:
            if not value in types:
                raise ValueError("Publication type [%s] is not allowed" % value)

        object.__setattr__(self, name, value)

    def date(self):
        s = ""
        if self.month is not None:
            s += self.month + " "
        if self.year is not None:
            s += self.year + " "
        return s.strip()


class Annotation(Object):
    """An annotation on a file"""
    def __init__(self, file, uuid, surrogate=True):
        super().__init__(uuid, surrogate)
        self.file = file




class File(Object):
    """A file (PDF, etc) associated to a document"""
    def __init__(self, uuid, surrogate=True):
        super().__init__(uuid, surrogate)
        self.title = None



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
        self.parent = None
        self.children = []
        self.publications = []
        self.local_uuid = uuid
        self.name = name

    def __str__(self):
        if self.parent is None:
            return "%s" % self.name
        return "%s -> %s" % (self.name, self.parent.uuid)


class Manager(Object):
    """A bibliographic manager"""
    pass