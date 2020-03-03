# coding: utf-8
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Annotation(Base):
    __tablename__ = "annotations"

    annotationID = Column(Integer, primary_key=True)
    itemID = Column(
        ForeignKey("items.itemID", ondelete="CASCADE"), nullable=False, index=True
    )
    parent = Column(Text)
    textNode = Column(Integer)
    offset = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    cols = Column(Integer)
    rows = Column(Integer)
    text = Column(Text)
    collapsed = Column(Boolean)
    dateModified = Column(Date)

    # itemAttachment = relationship('ItemAttachment', primaryjoin='Annotation.itemID == ItemAttachment.itemID', backref='annotations')


class BaseFieldMapping(Base):
    __tablename__ = "baseFieldMappings"

    itemTypeID = Column(
        ForeignKey("itemTypes.itemTypeID"), primary_key=True, nullable=False
    )
    baseFieldID = Column(
        ForeignKey("fields.fieldID"), primary_key=True, nullable=False, index=True
    )
    fieldID = Column(
        ForeignKey("fields.fieldID"), primary_key=True, nullable=False, index=True
    )

    field = relationship(
        "Field",
        primaryjoin="BaseFieldMapping.baseFieldID == Field.fieldID",
        backref="field_base_field_mappings",
    )
    field1 = relationship(
        "Field",
        primaryjoin="BaseFieldMapping.fieldID == Field.fieldID",
        backref="field_base_field_mappings_0",
    )
    itemType = relationship(
        "ItemType",
        primaryjoin="BaseFieldMapping.itemTypeID == ItemType.itemTypeID",
        backref="base_field_mappings",
    )


class BaseFieldMappingsCombined(Base):
    __tablename__ = "baseFieldMappingsCombined"

    itemTypeID = Column(Integer, primary_key=True, nullable=False)
    baseFieldID = Column(Integer, primary_key=True, nullable=False, index=True)
    fieldID = Column(Integer, primary_key=True, nullable=False, index=True)


class Charset(Base):
    __tablename__ = "charsets"

    charsetID = Column(Integer, primary_key=True)
    charset = Column(Text, unique=True)


class CollectionItem(Base):
    __tablename__ = "collectionItems"

    collectionID = Column(
        ForeignKey("collections.collectionID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    itemID = Column(
        ForeignKey("items.itemID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    orderIndex = Column(Integer, nullable=False, server_default=FetchedValue())

    collection = relationship(
        "Collection",
        primaryjoin="CollectionItem.collectionID == Collection.collectionID",
        backref="collection_items",
    )
    item = relationship(
        "Item",
        primaryjoin="CollectionItem.itemID == Item.itemID",
        backref="collection_items",
    )


class CollectionRelation(Base):
    __tablename__ = "collectionRelations"

    collectionID = Column(
        ForeignKey("collections.collectionID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    predicateID = Column(
        ForeignKey("relationPredicates.predicateID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    object = Column(Text, primary_key=True, nullable=False, index=True)

    collection = relationship(
        "Collection",
        primaryjoin="CollectionRelation.collectionID == Collection.collectionID",
        backref="collection_relations",
    )
    relationPredicate = relationship(
        "RelationPredicate",
        primaryjoin="CollectionRelation.predicateID == RelationPredicate.predicateID",
        backref="collection_relations",
    )


class Collection(Base):
    __tablename__ = "collections"
    __table_args__ = (UniqueConstraint("libraryID", "key"),)

    collectionID = Column(Integer, primary_key=True)
    collectionName = Column(Text, nullable=False)
    parentCollectionID = Column(
        ForeignKey("collections.collectionID", ondelete="CASCADE"),
        server_default=FetchedValue(),
    )
    clientDateModified = Column(DateTime, nullable=False, server_default=FetchedValue())
    libraryID = Column(
        ForeignKey("libraries.libraryID", ondelete="CASCADE"), nullable=False
    )
    key = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, server_default=FetchedValue())
    synced = Column(Integer, nullable=False, index=True, server_default=FetchedValue())

    library = relationship(
        "Library",
        primaryjoin="Collection.libraryID == Library.libraryID",
        backref="collections",
    )
    parent = relationship(
        "Collection",
        remote_side=[collectionID],
        primaryjoin="Collection.parentCollectionID == Collection.collectionID",
        backref="collections",
    )


class CreatorType(Base):
    __tablename__ = "creatorTypes"

    creatorTypeID = Column(Integer, primary_key=True)
    creatorType = Column(Text)


class Creator(Base):
    __tablename__ = "creators"
    __table_args__ = (UniqueConstraint("lastName", "firstName", "fieldMode"),)

    creatorID = Column(Integer, primary_key=True)
    firstName = Column(Text)
    lastName = Column(Text)
    fieldMode = Column(Integer)


class CustomBaseFieldMapping(Base):
    __tablename__ = "customBaseFieldMappings"

    customItemTypeID = Column(
        ForeignKey("customItemTypes.customItemTypeID"), primary_key=True, nullable=False
    )
    baseFieldID = Column(
        ForeignKey("fields.fieldID"), primary_key=True, nullable=False, index=True
    )
    customFieldID = Column(
        ForeignKey("customFields.customFieldID"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    field = relationship(
        "Field",
        primaryjoin="CustomBaseFieldMapping.baseFieldID == Field.fieldID",
        backref="custom_base_field_mappings",
    )
    customField = relationship(
        "CustomField",
        primaryjoin="CustomBaseFieldMapping.customFieldID == CustomField.customFieldID",
        backref="custom_base_field_mappings",
    )
    customItemType = relationship(
        "CustomItemType",
        primaryjoin="CustomBaseFieldMapping.customItemTypeID == CustomItemType.customItemTypeID",
        backref="custom_base_field_mappings",
    )


class CustomField(Base):
    __tablename__ = "customFields"

    customFieldID = Column(Integer, primary_key=True)
    fieldName = Column(Text)
    label = Column(Text)


class CustomItemTypeField(Base):
    __tablename__ = "customItemTypeFields"

    customItemTypeID = Column(
        ForeignKey("customItemTypes.customItemTypeID"), primary_key=True, nullable=False
    )
    fieldID = Column(ForeignKey("fields.fieldID"), index=True)
    customFieldID = Column(ForeignKey("customFields.customFieldID"), index=True)
    hide = Column(Integer, nullable=False)
    orderIndex = Column(Integer, primary_key=True, nullable=False)

    customField = relationship(
        "CustomField",
        primaryjoin="CustomItemTypeField.customFieldID == CustomField.customFieldID",
        backref="custom_item_type_fields",
    )
    customItemType = relationship(
        "CustomItemType",
        primaryjoin="CustomItemTypeField.customItemTypeID == CustomItemType.customItemTypeID",
        backref="custom_item_type_fields",
    )
    field = relationship(
        "Field",
        primaryjoin="CustomItemTypeField.fieldID == Field.fieldID",
        backref="custom_item_type_fields",
    )


class CustomItemType(Base):
    __tablename__ = "customItemTypes"

    customItemTypeID = Column(Integer, primary_key=True)
    typeName = Column(Text)
    label = Column(Text)
    display = Column(Integer, server_default=FetchedValue())
    icon = Column(Text)


class FieldFormat(Base):
    __tablename__ = "fieldFormats"

    fieldFormatID = Column(Integer, primary_key=True)
    regex = Column(Text)
    isInteger = Column(Integer)


class Field(Base):
    __tablename__ = "fields"

    fieldID = Column(Integer, primary_key=True)
    fieldName = Column(Text)
    fieldFormatID = Column(ForeignKey("fieldFormats.fieldFormatID"))

    fieldFormat = relationship(
        "FieldFormat",
        primaryjoin="Field.fieldFormatID == FieldFormat.fieldFormatID",
        backref="fields",
    )


class FieldsCombined(Base):
    __tablename__ = "fieldsCombined"

    fieldID = Column(Integer, primary_key=True)
    fieldName = Column(Text, nullable=False)
    label = Column(Text)
    fieldFormatID = Column(Integer)
    custom = Column(Integer, nullable=False)


class FileTypeMimeType(Base):
    __tablename__ = "fileTypeMimeTypes"

    fileTypeID = Column(
        ForeignKey("fileTypes.fileTypeID"), primary_key=True, nullable=False
    )
    mimeType = Column(Text, primary_key=True, nullable=False, index=True)

    fileType = relationship(
        "FileType",
        primaryjoin="FileTypeMimeType.fileTypeID == FileType.fileTypeID",
        backref="file_type_mime_types",
    )


class FileType(Base):
    __tablename__ = "fileTypes"

    fileTypeID = Column(Integer, primary_key=True)
    fileType = Column(Text, unique=True)


t_fulltextItemWords = Table(
    "fulltextItemWords",
    metadata,
    Column(
        "wordID", ForeignKey("fulltextWords.wordID"), primary_key=True, nullable=False
    ),
    Column(
        "itemID",
        ForeignKey("items.itemID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    ),
)


class FulltextWord(Base):
    __tablename__ = "fulltextWords"

    wordID = Column(Integer, primary_key=True)
    word = Column(Text, unique=True)


class Group(Base):
    __tablename__ = "groups"

    groupID = Column(Integer, primary_key=True)
    libraryID = Column(
        ForeignKey("libraries.libraryID", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)

    library = relationship(
        "Library",
        uselist=False,
        primaryjoin="Group.libraryID == Library.libraryID",
        backref="groups",
    )


class Highlight(Base):
    __tablename__ = "highlights"

    highlightID = Column(Integer, primary_key=True)
    itemID = Column(
        ForeignKey("item.itemID", ondelete="CASCADE"), nullable=False, index=True
    )
    startParent = Column(Text)
    startTextNode = Column(Integer)
    startOffset = Column(Integer)
    endParent = Column(Text)
    endTextNode = Column(Integer)
    endOffset = Column(Integer)
    dateModified = Column(Date)

    # itemAttachment = relationship('ItemAttachment', primaryjoin='Highlight.itemID == ItemAttachment.itemID', backref='highlights')


class ItemCreator(Base):
    __tablename__ = "itemCreators"
    __table_args__ = (UniqueConstraint("itemID", "orderIndex"),)

    itemID = Column(
        ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    creatorID = Column(
        ForeignKey("creators.creatorID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    creatorTypeID = Column(
        ForeignKey("creatorTypes.creatorTypeID"),
        primary_key=True,
        nullable=False,
        index=True,
        server_default=FetchedValue(),
    )
    orderIndex = Column(
        Integer, primary_key=True, nullable=False, server_default=FetchedValue()
    )

    creator = relationship(
        "Creator",
        primaryjoin="ItemCreator.creatorID == Creator.creatorID",
        backref="item_creators",
    )
    creatorType = relationship(
        "CreatorType",
        primaryjoin="ItemCreator.creatorTypeID == CreatorType.creatorTypeID",
        backref="item_creators",
    )
    item = relationship(
        "Item", primaryjoin="ItemCreator.itemID == Item.itemID", backref="creators"
    )


class ItemData(Base):
    __tablename__ = "itemData"

    itemID = Column(
        ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    fieldID = Column(
        ForeignKey("fieldsCombined.fieldID"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    valueID = Column(ForeignKey("itemDataValues.valueID"))

    field = relationship(
        "FieldsCombined",
        primaryjoin="ItemData.fieldID == FieldsCombined.fieldID",
        backref="item_data",
    )
    item = relationship(
        "Item", primaryjoin="ItemData.itemID == Item.itemID", backref="data"
    )
    data = relationship(
        "ItemDataValue",
        primaryjoin="ItemData.valueID == ItemDataValue.valueID",
        backref="item_data",
    )


class ItemDataValue(Base):
    __tablename__ = "itemDataValues"
    valueID = Column(Integer, primary_key=True)
    value = Column(Text)

    data = relationship("ItemData", backref="value")


class ItemRelation(Base):
    __tablename__ = "itemRelations"

    itemID = Column(
        ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    predicateID = Column(
        ForeignKey("relationPredicates.predicateID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    object = Column(Text, primary_key=True, nullable=False, index=True)

    item = relationship(
        "Item",
        primaryjoin="ItemRelation.itemID == Item.itemID",
        backref="item_relations",
    )
    relationPredicate = relationship(
        "RelationPredicate",
        primaryjoin="ItemRelation.predicateID == RelationPredicate.predicateID",
        backref="item_relations",
    )


class ItemTag(Base):
    __tablename__ = "itemTags"

    itemID = Column(
        ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    tagID = Column(
        ForeignKey("tags.tagID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    type = Column(Integer, nullable=False)

    item = relationship(
        "Item", primaryjoin="ItemTag.itemID == Item.itemID", backref="item_tags"
    )
    tag = relationship(
        "Tag", primaryjoin="ItemTag.tagID == Tag.tagID", backref="item_tags"
    )


class ItemTypeCreatorType(Base):
    __tablename__ = "itemTypeCreatorTypes"

    itemTypeID = Column(
        ForeignKey("itemTypes.itemTypeID"), primary_key=True, nullable=False
    )
    creatorTypeID = Column(
        ForeignKey("creatorTypes.creatorTypeID"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    primaryField = Column(Integer)

    creatorType = relationship(
        "CreatorType",
        primaryjoin="ItemTypeCreatorType.creatorTypeID == CreatorType.creatorTypeID",
        backref="item_type_creator_types",
    )
    itemType = relationship(
        "ItemType",
        primaryjoin="ItemTypeCreatorType.itemTypeID == ItemType.itemTypeID",
        backref="item_type_creator_types",
    )


class ItemTypeField(Base):
    __tablename__ = "itemTypeFields"
    __table_args__ = (UniqueConstraint("itemTypeID", "fieldID"),)

    itemTypeID = Column(
        ForeignKey("itemTypes.itemTypeID"), primary_key=True, nullable=False
    )
    fieldID = Column(ForeignKey("fields.fieldID"), index=True)
    hide = Column(Integer)
    orderIndex = Column(Integer, primary_key=True, nullable=False)

    field = relationship(
        "Field",
        primaryjoin="ItemTypeField.fieldID == Field.fieldID",
        backref="item_type_fields",
    )
    itemType = relationship(
        "ItemType",
        primaryjoin="ItemTypeField.itemTypeID == ItemType.itemTypeID",
        backref="item_type_fields",
    )


class ItemTypeFieldsCombined(Base):
    __tablename__ = "itemTypeFieldsCombined"
    __table_args__ = (UniqueConstraint("itemTypeID", "fieldID"),)

    itemTypeID = Column(Integer, primary_key=True, nullable=False)
    fieldID = Column(Integer, nullable=False, index=True)
    hide = Column(Integer)
    orderIndex = Column(Integer, primary_key=True, nullable=False)


class ItemType(Base):
    __tablename__ = "itemTypes"

    itemTypeID = Column(Integer, primary_key=True)
    typeName = Column(Text)
    templateItemTypeID = Column(Integer)
    display = Column(Integer, server_default=FetchedValue())


class ItemTypesCombined(Base):
    __tablename__ = "itemTypesCombined"

    itemTypeID = Column(Integer, primary_key=True)
    typeName = Column(Text, nullable=False)
    display = Column(Integer, nullable=False, server_default=FetchedValue())
    custom = Column(Integer, nullable=False)


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (UniqueConstraint("libraryID", "key"),)

    itemID = Column(Integer, primary_key=True)
    itemTypeID = Column(Integer, nullable=False)
    dateAdded = Column(DateTime, nullable=False, server_default=FetchedValue())
    dateModified = Column(DateTime, nullable=False, server_default=FetchedValue())
    clientDateModified = Column(DateTime, nullable=False, server_default=FetchedValue())
    libraryID = Column(
        ForeignKey("libraries.libraryID", ondelete="CASCADE"), nullable=False
    )
    key = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, server_default=FetchedValue())
    synced = Column(Integer, nullable=False, index=True, server_default=FetchedValue())

    library = relationship(
        "Library", primaryjoin="Item.libraryID == Library.libraryID", backref="items"
    )
    # fulltextWords = relationship('FulltextWord', secondary='YARK.fulltextItemWords', backref='items')


class DeletedItem(Item):
    __tablename__ = "deletedItems"

    itemID = Column(ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True)
    dateDeleted = Column(
        NullType, nullable=False, index=True, server_default=FetchedValue()
    )


class FeedItem(Item):
    __tablename__ = "feedItems"

    itemID = Column(ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True)
    guid = Column(Text, nullable=False, unique=True)
    readTime = Column(DateTime)
    translatedTime = Column(DateTime)


class FulltextItem(Item):
    __tablename__ = "fulltextItems"

    itemID = Column(ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True)
    indexedPages = Column(Integer)
    totalPages = Column(Integer)
    indexedChars = Column(Integer)
    totalChars = Column(Integer)
    version = Column(Integer, nullable=False, index=True, server_default=FetchedValue())
    # synced = Column(Integer, nullable=False, index=True, server_default=FetchedValue())


class GroupItem(Item):
    __tablename__ = "groupItems"

    itemID = Column(ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True)
    createdByUserID = Column(ForeignKey("users.userID", ondelete="SET NULL"))
    lastModifiedByUserID = Column(ForeignKey("users.userID", ondelete="SET NULL"))

    user = relationship(
        "User",
        primaryjoin="GroupItem.createdByUserID == User.userID",
        backref="user_group_items",
    )
    user1 = relationship(
        "User",
        primaryjoin="GroupItem.lastModifiedByUserID == User.userID",
        backref="user_group_items_0",
    )


class ItemAttachment(Base):
    __tablename__ = "itemAttachments"

    itemID = Column(ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True)
    parentItemID = Column(ForeignKey("items.itemID"), index=True)
    linkMode = Column(Integer)
    contentType = Column(Text, index=True)
    charsetID = Column(
        ForeignKey("charsets.charsetID", ondelete="SET NULL"), index=True
    )
    path = Column(Text)
    syncState = Column(Integer, index=True, server_default=FetchedValue())
    storageModTime = Column(Integer)
    storageHash = Column(Text)

    parent = relationship("Item", foreign_keys=[parentItemID], backref="attachments")

    # charset = relationship('Charset', primaryjoin='ItemAttachment.charsetID == Charset.charsetID', backref='item_attachments')
    # item = relationship(Item, primaryjoin='ItemAttachment.parentItemID == Item.itemID', backref='item_children')


class ItemNote(Base):
    __tablename__ = "itemNotes"

    itemID = Column(ForeignKey("items.itemID", ondelete="CASCADE"), primary_key=True)
    parentItemID = Column(ForeignKey("items.itemID"), index=True)
    note = Column(Text)
    title = Column(Text)

    parentItem = relationship("Item", foreign_keys=[parentItemID], backref="notes")


class Library(Base):
    __tablename__ = "libraries"

    libraryID = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False)
    editable = Column(Integer, nullable=False)
    filesEditable = Column(Integer, nullable=False)
    version = Column(Integer, nullable=False, server_default=FetchedValue())
    storageVersion = Column(Integer, nullable=False, server_default=FetchedValue())
    lastSync = Column(Integer, nullable=False, server_default=FetchedValue())
    archived = Column(Integer, nullable=False, server_default=FetchedValue())


class Feed(Library):
    __tablename__ = "feeds"

    libraryID = Column(
        ForeignKey("libraries.libraryID", ondelete="CASCADE"), primary_key=True
    )
    name = Column(Text, nullable=False)
    url = Column(Text, nullable=False, unique=True)
    lastUpdate = Column(DateTime)
    lastCheck = Column(DateTime)
    lastCheckError = Column(Text)
    cleanupReadAfter = Column(Integer)
    cleanupUnreadAfter = Column(Integer)
    refreshInterval = Column(Integer)


class Proxy(Base):
    __tablename__ = "proxies"

    proxyID = Column(Integer, primary_key=True)
    multiHost = Column(Integer)
    autoAssociate = Column(Integer)
    scheme = Column(Text)


class ProxyHost(Base):
    __tablename__ = "proxyHosts"

    hostID = Column(Integer, primary_key=True)
    proxyID = Column(ForeignKey("proxies.proxyID"), index=True)
    hostname = Column(Text)

    proxy = relationship(
        "Proxy", primaryjoin="ProxyHost.proxyID == Proxy.proxyID", backref="proxy_hosts"
    )


class PublicationsItem(Base):
    __tablename__ = "publicationsItems"

    itemID = Column(Integer, primary_key=True)


class RelationPredicate(Base):
    __tablename__ = "relationPredicates"

    predicateID = Column(Integer, primary_key=True)
    predicate = Column(Text, unique=True)


class SavedSearchCondition(Base):
    __tablename__ = "savedSearchConditions"

    savedSearchID = Column(
        ForeignKey("savedSearches.savedSearchID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    searchConditionID = Column(Integer, primary_key=True, nullable=False)
    condition = Column(Text, nullable=False)
    operator = Column(Text)
    value = Column(Text)
    required = Column(Numeric)

    savedSearch = relationship(
        "SavedSearch",
        primaryjoin="SavedSearchCondition.savedSearchID == SavedSearch.savedSearchID",
        backref="saved_search_conditions",
    )


class SavedSearch(Base):
    __tablename__ = "savedSearches"
    __table_args__ = (UniqueConstraint("libraryID", "key"),)

    savedSearchID = Column(Integer, primary_key=True)
    savedSearchName = Column(Text, nullable=False)
    clientDateModified = Column(DateTime, nullable=False, server_default=FetchedValue())
    libraryID = Column(
        ForeignKey("libraries.libraryID", ondelete="CASCADE"), nullable=False
    )
    key = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, server_default=FetchedValue())
    synced = Column(Integer, nullable=False, index=True, server_default=FetchedValue())

    library = relationship(
        "Library",
        primaryjoin="SavedSearch.libraryID == Library.libraryID",
        backref="saved_searches",
    )


class Setting(Base):
    __tablename__ = "settings"

    setting = Column(Text, primary_key=True, nullable=False)
    key = Column(Text, primary_key=True, nullable=False)
    value = Column(NullType)


class StorageDeleteLog(Base):
    __tablename__ = "storageDeleteLog"

    libraryID = Column(
        ForeignKey("libraries.libraryID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    key = Column(Text, primary_key=True, nullable=False)
    dateDeleted = Column(Text, nullable=False, server_default=FetchedValue())

    library = relationship(
        "Library",
        primaryjoin="StorageDeleteLog.libraryID == Library.libraryID",
        backref="storage_delete_logs",
    )


class SyncCache(Base):
    __tablename__ = "syncCache"

    libraryID = Column(
        ForeignKey("libraries.libraryID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    key = Column(Text, primary_key=True, nullable=False)
    syncObjectTypeID = Column(
        ForeignKey("syncObjectTypes.syncObjectTypeID"), primary_key=True, nullable=False
    )
    version = Column(Integer, primary_key=True, nullable=False)
    data = Column(Text)

    library = relationship(
        "Library",
        primaryjoin="SyncCache.libraryID == Library.libraryID",
        backref="sync_caches",
    )
    syncObjectType = relationship(
        "SyncObjectType",
        primaryjoin="SyncCache.syncObjectTypeID == SyncObjectType.syncObjectTypeID",
        backref="sync_caches",
    )


t_syncDeleteLog = Table(
    "syncDeleteLog",
    metadata,
    Column(
        "syncObjectTypeID",
        ForeignKey("syncObjectTypes.syncObjectTypeID"),
        nullable=False,
    ),
    Column(
        "libraryID",
        ForeignKey("libraries.libraryID", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("key", Text, nullable=False),
    Column("dateDeleted", Text, nullable=False, server_default=FetchedValue()),
    UniqueConstraint("syncObjectTypeID", "libraryID", "key"),
)


class SyncObjectType(Base):
    __tablename__ = "syncObjectTypes"

    syncObjectTypeID = Column(Integer, primary_key=True)
    name = Column(Text, index=True)


class SyncQueue(Base):
    __tablename__ = "syncQueue"

    libraryID = Column(
        ForeignKey("libraries.libraryID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    key = Column(Text, primary_key=True, nullable=False)
    syncObjectTypeID = Column(
        ForeignKey("syncObjectTypes.syncObjectTypeID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    lastCheck = Column(DateTime)
    tries = Column(Integer)

    library = relationship(
        "Library",
        primaryjoin="SyncQueue.libraryID == Library.libraryID",
        backref="sync_queues",
    )
    syncObjectType = relationship(
        "SyncObjectType",
        primaryjoin="SyncQueue.syncObjectTypeID == SyncObjectType.syncObjectTypeID",
        backref="sync_queues",
    )


class SyncedSetting(Base):
    __tablename__ = "syncedSettings"

    setting = Column(Text, primary_key=True, nullable=False)
    libraryID = Column(
        ForeignKey("libraries.libraryID", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    value = Column(NullType, nullable=False)
    version = Column(Integer, nullable=False, server_default=FetchedValue())
    synced = Column(Integer, nullable=False, server_default=FetchedValue())

    library = relationship(
        "Library",
        primaryjoin="SyncedSetting.libraryID == Library.libraryID",
        backref="synced_settings",
    )


class Tag(Base):
    __tablename__ = "tags"

    tagID = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)


class TransactionLog(Base):
    __tablename__ = "transactionLog"

    transactionID = Column(
        ForeignKey("transactions.transactionID"), primary_key=True, nullable=False
    )
    field = Column(Text, primary_key=True, nullable=False)
    value = Column(Numeric, primary_key=True, nullable=False)

    transaction = relationship(
        "Transaction",
        primaryjoin="TransactionLog.transactionID == Transaction.transactionID",
        backref="transaction_logs",
    )


class TransactionSet(Base):
    __tablename__ = "transactionSets"

    transactionSetID = Column(Integer, primary_key=True)
    event = Column(Text)
    id = Column(Integer)


class Transaction(Base):
    __tablename__ = "transactions"

    transactionID = Column(Integer, primary_key=True)
    transactionSetID = Column(Integer, index=True)
    context = Column(Text)
    action = Column(Text)


class TranslatorCache(Base):
    __tablename__ = "translatorCache"

    fileName = Column(Text, primary_key=True)
    metadataJSON = Column(Text)
    lastModifiedTime = Column(Integer)


class User(Base):
    __tablename__ = "users"

    userID = Column(Integer, primary_key=True)
    username = Column(Text, nullable=False)


class Version(Base):
    __tablename__ = "version"

    schema = Column(Text, primary_key=True, index=True)
    version = Column(Integer, nullable=False)
