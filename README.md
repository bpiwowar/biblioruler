The goal of this project is to create a common interface to the different bibliography managers, allowing to easily import bibliographies from Mendeley, Papers 3, or Zotero and 

1. Export them to native formats (e.g. Zotero RDF) that can be imported without loss

# Current conversions

## Supported Inputs

## Mendeley

What is imported:

- Title, year, authors
- Conference title, 
- Keywords and Note
- PDF and their annotations

## Papers 3 (unknown status)

The code has not been updated for a while, so it might or might not work

## Zotero 5 

Basic support (to retrieve papers) 

## Supported output

### Annotated PDF using PyPDF2

### Zotero RDF

Zotero RDF export is almost functional. I advice you test it by using a test profile in Zotero, to check first if everything is going well, before importing it in your main library.

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
