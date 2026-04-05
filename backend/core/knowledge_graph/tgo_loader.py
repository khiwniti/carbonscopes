"""Utility functions for loading TGO emission factor data into GraphDB.

The loader expects a list of material dictionaries with the following keys:
- id: unique URI fragment (e.g., "materials/concrete-c30")
- name_en / name_th: bilingual labels
- emission_factor: decimal value
- unit: unit string (e.g., "kgCO2e/kg")
- category: material category string
- effective_date: ISO date string
- source_document: URI string
"""

import json
from pathlib import Path
from typing import List, Dict

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# Namespace for TGO ontology
TGO = Namespace("http://tgo.or.th/ontology#")


def _material_to_triples(material: Dict) -> List[tuple]:
    """Convert a material dict to a list of RDF triples.
    Returns a list of (subject, predicate, object) tuples.
    """
    uri = URIRef(f"http://tgo.or.th/{material['id']}")
    triples = []
    # Type
    triples.append((uri, RDF.type, TGO.ConstructionMaterial))
    # Labels (English and Thai)
    if "name_en" in material:
        triples.append((uri, RDFS.label, Literal(material["name_en"], lang="en")))
    if "name_th" in material:
        triples.append((uri, RDFS.label, Literal(material["name_th"], lang="th")))
    # Emission factor
    triples.append(
        (
            uri,
            TGO.hasEmissionFactor,
            Literal(str(material["emission_factor"]), datatype=XSD.decimal),
        )
    )
    # Unit
    triples.append((uri, TGO.hasUnit, Literal(material["unit"], datatype=XSD.string)))
    # Category
    triples.append(
        (uri, TGO.category, Literal(material["category"], datatype=XSD.string))
    )
    # Effective date
    triples.append(
        (uri, TGO.effectiveDate, Literal(material["effective_date"], datatype=XSD.date))
    )
    # Source document
    triples.append((uri, TGO.sourceDocument, URIRef(material["source_document"])))
    return triples


def load_materials(materials: List[Dict], graph: Graph) -> None:
    """Load a list of material dictionaries into the provided RDFLib Graph.
    The graph is expected to be bound to the GraphDB SPARQL endpoint.
    """
    for m in materials:
        triples = _material_to_triples(m)
        for s, p, o in triples:
            graph.add((s, p, o))


def load_from_json_file(json_path: Path, graph: Graph) -> None:
    """Read a JSON file containing a list of material objects and load them.
    The JSON file should be an array of objects matching the expected material schema.
    """
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("TGO JSON file must contain a list of materials")
    load_materials(data, graph)
