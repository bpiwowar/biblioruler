The goal of this project is to create a common interface to the different bibliography managers, allowing to easily import bibliographies from Mendeley, Papers 3, or Zotero. One of the main objective is to switch as easily as possible from one to the other.

Please see below for the status of the different importers and exporters.

# Current conversions

## Supported Inputs

### Mendeley

What is imported:

- title
- year
- authors
- conference/journal title
- keywords
- note
- volume
- pages
- DOI
- PDF and their annotations
- collections (folders)

### Papers 3 (unknown status)

The code has not been updated for a while, so it might or might not work

### Zotero 5 

Basic support (to retrieve papers) 

## Supported output


### Annotated PDF using PyPDF2

### Zotero RDF

Zotero RDF export is functional. I advice you test it by using a test profile in Zotero, to check first if everything is going well, before importing it in your main library. 
Supported fields:

- title
- conference/journal title
- authors
- DOI
- volume
- number
- pages
- keywords (tags)
- notes
- collections


# Exemples

## Export Mendeley to Zotero-RDF with annotated PDFs

```
python3  -m biblioruler export mendeley zotero_rdf <basename> --exporter-annotate
```
where `basename` is the name the folder where PDF will be stored, and also the basename of the RDF file `basename.rdf`.


# Information

The underlying model for references is [the PURL schema](http://vocab.org/biblio/schema)

Other resources:

- [CSL Schema](https://github.com/citation-style-language/schema/raw/master/csl-data.json)
- [Mapping between Zotero and CSL](http://aurimasv.github.io/z2csl/typeMap.xml)
