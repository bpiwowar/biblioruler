#
# Common classes for bibliography managers
#

"""All the types that can be taken by a paper"""
types = set(["article", "article-journal", "article-magazine", "article-newspaper",
    "bill", "book", "broadcast", "chapter", "dataset", "entry", "entry-dictionary",
    "entry-encyclopedia", "figure", "graphic", "interview", "journal", "legal_case", "legislation",
    "manuscript", "map", "motion_picture", "musical_score", "pamphlet", "paper-conference", "proceedings", "patent",
    "personal_communication", "post", "post-weblog", "report", "review", "review-book", "song", "speech",
    "thesis", "treaty", "webpage"])


class Paper(object):
    """A paper"""
    def __init__(self, uuid, type):
        self.uuid = uuid
        self.type = type
        self.authors = []
        self.keywords = set()

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


class File(object):
    """A file (PDF, etc) associated to a document"""
    pass


class Author(object):
    """The author of a paper"""
    def __init__(self, uuid, firstname, surname):
        self.uuid = uuid
        self.firstname = firstname
        self.surname = surname


class Keyword(object):
    """A keyword"""
    def __init__(self, uuid, name):
        self.parent = None
        self.uuid = uuid
        self.name = name


class Collection(object):
    """A collection of publications"""
    def __init__(self, uuid, name):
        self.parent = None
        self.children = []
        self.publications = []
        self.uuid = uuid
        self.name = name

    def __str__(self):
        if self.parent is None:
            return "%s" % self.name
        return "%s -> %s" % (self.name, self.parent.uuid)


class Manager(object):
    """A bibliographic manager"""
    pass