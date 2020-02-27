# coding: utf-8
from sqlalchemy import Column, Float, ForeignKey, Integer, LargeBinary, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import FetchedValue
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Annotation(Base):
    __tablename__ = "Annotation"

    ROWID = Column(Integer, primary_key=True)
    color = Column(Integer)
    contents = Column(Text)
    created_at = Column(Float, index=True)
    created_by = Column(Text, index=True)
    dictionary = Column(LargeBinary)
    extensible_properties = Column(LargeBinary)
    external = Column(Integer)
    first_text_index = Column(Integer)
    flagged = Column(Integer)
    height = Column(Float)
    hidden = Column(Integer)
    is_mine = Column(Integer)
    left = Column(Float)
    object_id = Column(ForeignKey("PDF.uuid", ondelete="CASCADE"), index=True)
    page_nr = Column(Integer, index=True)
    path = Column(Text)
    position = Column(Text)
    privacy_level = Column(Integer)
    rectangles = Column(LargeBinary)
    lines_as_strings = Column(LargeBinary)
    line_width = Column(Float)
    searchresult = Column(Integer)
    selection = Column(Text, index=True)
    target_name = Column(Text)
    target_page_nr = Column(Integer)
    target_rectangle = Column(LargeBinary)
    target_url = Column(Text)
    text = Column(Text)
    text_range_length = Column(Integer)
    top = Column(Float)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    url = Column(Text, index=True)
    uuid = Column(Text, nullable=False, unique=True)
    width = Column(Float)

    object = relationship(
        "PDF", primaryjoin="Annotation.object_id == PDF.uuid", backref="annotations"
    )


class Author(Base):
    __tablename__ = "Author"

    ROWID = Column(Integer, primary_key=True)
    affiliation = Column(Text, index=True)
    created_at = Column(Float, index=True)
    email = Column(Text, index=True)
    extensible_properties = Column(LargeBinary)
    flagged = Column(Integer)
    fullname = Column(Text, index=True)
    initial = Column(Text, index=True)
    institutional = Column(Integer)
    is_me = Column(Integer)
    label = Column(Integer, index=True)
    location = Column(Text, index=True)
    name_string = Column(Text, index=True)
    nickname = Column(Text, index=True)
    notes = Column(Text)
    post_title = Column(Text)
    pre_title = Column(Text)
    prename = Column(Text, index=True)
    privacy_level = Column(Integer)
    publication_count = Column(Integer, index=True)
    refreshed_at = Column(Float, index=True)
    role1 = Column(Integer)
    role2 = Column(Integer)
    role3 = Column(Integer)
    role4 = Column(Integer)
    role5 = Column(Integer)
    searchresult = Column(Integer)
    standard_name = Column(Text, index=True)
    surname = Column(Text, index=True)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)


class Bookmark(Base):
    __tablename__ = "Bookmark"

    ROWID = Column(Integer, primary_key=True)
    created_at = Column(Float, index=True)
    extensible_properties = Column(LargeBinary)
    page_nr = Column(Integer, index=True)
    pdf_id = Column(ForeignKey("PDF.uuid", ondelete="CASCADE"), index=True)
    position = Column(Text)
    title = Column(Text)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)
    zoomfactor = Column(Float)

    pdf = relationship(
        "PDF", primaryjoin="Bookmark.pdf_id == PDF.uuid", backref="bookmarks"
    )


class Citation(Base):
    __tablename__ = "Citation"

    ROWID = Column(Integer, primary_key=True)
    citekey = Column(Text, index=True)
    citekey_format = Column(Integer)
    created_at = Column(Float, index=True)
    created_by = Column(Text, index=True)
    extensible_properties = Column(LargeBinary)
    flagged = Column(Integer)
    is_mine = Column(Integer)
    object_id = Column(ForeignKey("Publication.uuid", ondelete="NO ACTION"), index=True)
    priority = Column(Integer, index=True)
    privacy_level = Column(Integer)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)

    object = relationship(
        "Publication",
        primaryjoin="Citation.object_id == Publication.uuid",
        backref="citations",
    )


class CitationItem(Base):
    __tablename__ = "CitationItem"

    ROWID = Column(Integer, primary_key=True)
    citation = Column(ForeignKey("Citation.uuid", ondelete="NO ACTION"), index=True)
    created_at = Column(Float, index=True)
    extensible_properties = Column(LargeBinary)
    locator = Column(Text)
    locator_type = Column(Integer, index=True)
    notes = Column(Text)
    object_id = Column(ForeignKey("Publication.uuid", ondelete="NO ACTION"), index=True)
    prefix = Column(Text)
    priority = Column(Integer, index=True)
    show_authors = Column(Integer)
    suffix = Column(Text)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)

    Citation = relationship(
        "Citation",
        primaryjoin="CitationItem.citation == Citation.uuid",
        backref="citation_items",
    )
    object = relationship(
        "Publication",
        primaryjoin="CitationItem.object_id == Publication.uuid",
        backref="citation_items",
    )


class Collection(Base):
    __tablename__ = "Collection"

    ROWID = Column(Integer, primary_key=True)
    collection_description = Column(Text)
    configuration = Column(LargeBinary)
    created_at = Column(Float, index=True)
    editable = Column(Integer)
    extensible_properties = Column(LargeBinary)
    icon_name = Column(Text)
    name = Column(Text, index=True)
    parent = Column(ForeignKey("Collection.uuid", ondelete="CASCADE"), index=True)
    priority = Column(Integer, index=True)
    privacy_level = Column(Integer)
    type = Column(Integer, index=True)
    update_count = Column(Integer)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)

    parent1 = relationship(
        "Collection",
        remote_side=[ROWID],
        primaryjoin="Collection.parent == Collection.uuid",
        backref="collections",
    )


class CollectionItem(Base):
    __tablename__ = "CollectionItem"

    ROWID = Column(Integer, primary_key=True)
    collection = Column(ForeignKey("Collection.uuid", ondelete="CASCADE"), index=True)
    created_at = Column(Float, index=True)
    extensible_properties = Column(LargeBinary)
    object_id = Column(ForeignKey("Publication.uuid", ondelete="CASCADE"), index=True)
    priority = Column(Integer, index=True)
    privacy_level = Column(Integer)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)

    Collection = relationship(
        "Collection",
        primaryjoin="CollectionItem.collection == Collection.uuid",
        backref="collection_items",
    )
    object = relationship(
        "Publication",
        primaryjoin="CollectionItem.object_id == Publication.uuid",
        backref="collection_items",
    )


class Keyword(Base):
    __tablename__ = "Keyword"

    ROWID = Column(Integer, primary_key=True)
    canonical_name = Column(Text, index=True)
    created_at = Column(Float, index=True)
    created_by = Column(Text, index=True)
    extensible_properties = Column(LargeBinary)
    is_mine = Column(Integer)
    name = Column(Text, index=True)
    parent = Column(ForeignKey("Keyword.uuid", ondelete="CASCADE"), index=True)
    publication_count = Column(Integer, index=True)
    searchresult = Column(Integer)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)

    parent1 = relationship(
        "Keyword",
        remote_side=[ROWID],
        primaryjoin="Keyword.parent == Keyword.uuid",
        backref="keywords",
    )


class KeywordItem(Base):
    __tablename__ = "KeywordItem"

    ROWID = Column(Integer, primary_key=True)
    assigned_by = Column(Text, index=True)
    created_at = Column(Float, index=True)
    extensible_properties = Column(LargeBinary)
    keyword_id = Column(ForeignKey("Keyword.uuid", ondelete="CASCADE"), index=True)
    object_id = Column(ForeignKey("Publication.uuid", ondelete="CASCADE"), index=True)
    priority = Column(Integer, index=True)
    privacy_level = Column(Integer)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)

    keyword = relationship(
        "Keyword",
        primaryjoin="KeywordItem.keyword_id == Keyword.uuid",
        backref="keyword_items",
    )
    object = relationship(
        "Publication",
        primaryjoin="KeywordItem.object_id == Publication.uuid",
        backref="keyword_items",
    )


class LocalMetadatum(Base):
    __tablename__ = "LocalMetadata"

    ROWID = Column(Integer, primary_key=True)
    data = Column(LargeBinary)
    key = Column(Text)
    uuid = Column(Text, nullable=False, unique=True)
    value = Column(Text)


t_Metadata = Table(
    "Metadata",
    metadata,
    Column("uuid", Text, nullable=False, unique=True),
    Column("data", LargeBinary),
    Column("key", Text, index=True),
    Column("value", Text),
)


class NameVariant(Base):
    __tablename__ = "NameVariant"

    ROWID = Column(Integer, primary_key=True)
    canonical_name = Column(Text, index=True)
    created_at = Column(Float, index=True)
    extensible_properties = Column(LargeBinary)
    name = Column(Text, index=True)
    object_id = Column(ForeignKey("Publication.uuid", ondelete="CASCADE"), index=True)
    preferred = Column(Integer)
    priority = Column(Integer, index=True)
    type = Column(Integer, index=True)
    updated_at = Column(Float)
    uuid = Column(Text, nullable=False, unique=True)

    object = relationship(
        "Publication",
        primaryjoin="NameVariant.object_id == Publication.uuid",
        backref="name_variants",
    )


class OrderedAuthor(Base):
    __tablename__ = "OrderedAuthor"

    ROWID = Column(Integer, primary_key=True)
    author_id = Column(ForeignKey("Author.uuid", ondelete="RESTRICT"), index=True)
    created_at = Column(Float, index=True)
    extensible_properties = Column(LargeBinary)
    is_primary = Column(Integer)
    object_id = Column(ForeignKey("Publication.uuid", ondelete="CASCADE"), index=True)
    priority = Column(Integer, index=True)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)

    author = relationship(
        "Author",
        primaryjoin="OrderedAuthor.author_id == Author.uuid",
        backref="ordered_authors",
    )
    object = relationship(
        "Publication",
        primaryjoin="OrderedAuthor.object_id == Publication.uuid",
        backref="ordered_authors",
    )


class PDF(Base):
    __tablename__ = "PDF"

    ROWID = Column(Integer, primary_key=True)
    caption = Column(Text)
    created_at = Column(Float, index=True)
    extensible_properties = Column(LargeBinary)
    fingerprint = Column(Text, index=True)
    is_alias = Column(Integer)
    is_primary = Column(Integer)
    md5 = Column(Text, index=True)
    mime_type = Column(Text, index=True)
    missing = Column(Integer)
    needs_ocr = Column(Integer)
    object_id = Column(ForeignKey("Publication.uuid", ondelete="CASCADE"), index=True)
    original_path = Column(Text)
    pages = Column(Integer)
    path = Column(Text, index=True)
    privacy_level = Column(Integer)
    rotation = Column(Integer)
    searchresult = Column(Integer)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)
    view_settings = Column(LargeBinary)

    object = relationship(
        "Publication", primaryjoin="PDF.object_id == Publication.uuid", backref="pdfs"
    )


class Publication(Base):
    __tablename__ = "Publication"

    ROWID = Column(Integer, primary_key=True)
    abbreviation = Column(Text, index=True)
    accepted_date = Column(Text, index=True)
    attributed_subtitle = Column(Text)
    attributed_title = Column(Text)
    author_string = Column(Text)
    author_year_string = Column(Text)
    body = Column(Text)
    bundle = Column(ForeignKey("Publication.uuid", ondelete="RESTRICT"))
    bundle_string = Column(Text)
    canonical_title = Column(Text)
    citekey = Column(Text, index=True)
    citekey_base = Column(Text, index=True)
    copyright = Column(Text)
    created_at = Column(Float, index=True)
    document_number = Column(Text)
    doi = Column(Text, index=True)
    draft = Column(Integer)
    editor_string = Column(Text)
    endpage = Column(Text, index=True)
    extensible_properties = Column(LargeBinary)
    factor = Column(Float, index=True)
    flagged = Column(Integer)
    full_author_string = Column(Text)
    full_editor_string = Column(Text)
    full_photographer_string = Column(Text)
    full_translator_string = Column(Text)
    imported_date = Column(Float, index=True)
    initial = Column(Text, index=True)
    institution = Column(Text)
    keyword_string = Column(Text)
    kind = Column(Text, index=True)
    label = Column(Integer, index=True)
    language = Column(Text)
    lastread_date = Column(Float, index=True)
    location = Column(Text, index=True)
    manuscript = Column(Integer)
    marked_deleted = Column(Integer)
    marked_duplicate = Column(Integer)
    marked_edited = Column(Integer)
    matched = Column(Integer)
    newly_added = Column(Integer)
    notes = Column(Text)
    number = Column(Text, index=True)
    open_access = Column(Integer)
    photographer_string = Column(Text)
    place = Column(Text, index=True)
    printed_date = Column(Float)
    privacy_level = Column(Integer)
    publication_count = Column(Integer, index=True)
    publication_date = Column(Text, index=True)
    publication_string = Column(Text)
    publisher = Column(Text, index=True)
    quality = Column(Integer)
    rating = Column(Integer, index=True)
    read_status = Column(Integer, index=True)
    refreshed_at = Column(Float, index=True)
    revision_date = Column(Text, index=True)
    searchresult = Column(Integer)
    startpage = Column(Text, index=True)
    status = Column(Text, index=True)
    submission_date = Column(Text, index=True)
    subtitle = Column(Text, index=True)
    subtype = Column(Integer, index=True)
    summary = Column(Text)
    tag_string = Column(Text)
    times_cited = Column(Integer)
    times_read = Column(Integer, index=True)
    title = Column(Text, index=True)
    translator_string = Column(Text)
    type = Column(Integer, index=True)
    update_count = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    user_label = Column(Text, index=True)
    uuid = Column(Text, nullable=False, unique=True)
    version = Column(Text, index=True)
    volume = Column(Text, index=True)

    parent = relationship(
        "Publication",
        remote_side=[ROWID],
        primaryjoin="Publication.bundle == Publication.uuid",
        backref="publications",
    )


class Review(Base):
    __tablename__ = "Review"

    ROWID = Column(Integer, primary_key=True)
    comment = Column(Text)
    content = Column(Text)
    created_at = Column(Float, index=True)
    created_by = Column(Text, index=True)
    extensible_properties = Column(LargeBinary)
    flagged = Column(Integer)
    is_mine = Column(Integer)
    object_id = Column(ForeignKey("Publication.uuid", ondelete="CASCADE"), index=True)
    parent = Column(ForeignKey("Review.uuid", ondelete="CASCADE"), index=True)
    privacy_level = Column(Integer)
    rating = Column(Integer, index=True)
    score = Column(Integer, index=True)
    searchresult = Column(Integer)
    status = Column(Text, index=True)
    type = Column(Integer, index=True)
    updated_at = Column(Float, index=True)
    uuid = Column(Text, nullable=False, unique=True)

    object = relationship(
        "Publication",
        primaryjoin="Review.object_id == Publication.uuid",
        backref="reviews",
    )
    parent1 = relationship(
        "Review",
        remote_side=[ROWID],
        primaryjoin="Review.parent == Review.uuid",
        backref="reviews",
    )


class SyncEvent(Base):
    __tablename__ = "SyncEvent"

    ROWID = Column(Integer, primary_key=True)
    created_at = Column(Float, index=True)
    details = Column(LargeBinary)
    device_id = Column(Text, index=True)
    extensible_properties = Column(LargeBinary)
    remote_id = Column(Text, index=True)
    source_id = Column(Text, index=True)
    subtype = Column(Integer, index=True)
    type = Column(Integer, index=True)
    updated_at = Column(Float)
    uuid = Column(Text, nullable=False, unique=True)


class UsageEvent(Base):
    __tablename__ = "UsageEvent"

    ROWID = Column(Integer, primary_key=True)
    count = Column(Integer, index=True)
    created_at = Column(Float, index=True)
    details = Column(LargeBinary)
    device_id = Column(Text, index=True)
    duration = Column(Integer, index=True)
    ended_at = Column(Float, index=True)
    extensible_properties = Column(LargeBinary)
    subtype = Column(Integer, index=True)
    type = Column(Integer, index=True)
    updated_at = Column(Float)
    uuid = Column(Text, nullable=False, unique=True)


class ChangeLog(Base):
    __tablename__ = "changeLog"

    ROWID = Column(Integer, primary_key=True)
    modifiedDate = Column(Float, nullable=False, index=True)
    modTable = Column(Text, nullable=False, index=True)
    modUUID = Column(Text, nullable=False, index=True)
    modType = Column(Integer, nullable=False, server_default=FetchedValue())
    modColumn = Column(Text, index=True)
    modValue = Column(Text, index=True)
    device = Column(Text)
    dbRevision = Column(Text, index=True)


class RevisionLog(Base):
    __tablename__ = "revisionLog"

    ROWID = Column(Integer, primary_key=True, unique=True)
    modifiedDate = Column(Float)
    uuid = Column(Text, nullable=False, unique=True)
    localParent = Column(Text)
    remoteParent = Column(Text)
    device = Column(Text)
