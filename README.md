The goal of this project is to create a common interface to the different bibliography managers, allowing to easily import bibliographies from Mendeley, Papers 3, or Zotero and 

1. Export them to native formats (e.g. Zotero RDF) that can be imported without loss

# Current conversions

## Supported Inputs

- Mendeley
- Papers (broken)

## Supported output

- Annotated PDF using PyPDF2
- Zotero RDF

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

# Roadmap

1. Use pypothesis to sync annotations
1. (maybe) Synchronize different bibliography softwares
