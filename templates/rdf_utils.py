import rdflib
import re
from typing import List, Tuple

def remove_all_namespaces(g: rdflib.Graph):
        #TODO create unbind method for graph
        g.namespace_manager.store._Memory__namespace = {}
        g.namespace_manager.store._Memory__prefix = {}


def workaround_namespace_bindings(g: rdflib.Graph, add_g: rdflib.Graph):
        #bind replace/override does not work
        # as soon as an automatically namespaces is created when adding a triple, the namespace cannot be replaced or overridden
        update_graph(g, add_g)
        bind_namespaces_to_g(g, get_new_namespaces(add_g))

def update_graph(in_place_graph: rdflib.Graph, new_graph: rdflib.Graph) -> None:
        #create temporary graph with all old and new triples
        for triple in new_graph:
                in_place_graph.add(triple)

def bind_namespaces_to_g(g: rdflib.Graph, ns: List[Tuple[str]]) -> None:
        for prefix, namespace in ns:
                g.namespace_manager.bind(prefix,  namespace , replace=True, override=True)

def get_new_namespaces(new_graph: rdflib.Graph):
        return [(prefix, namespace.toPython()) for (prefix, namespace) in new_graph.namespaces()]


def get_ns_from_string(query: str) -> List[Tuple[str,str]]:
    pattern = ("(#)?[\s]*((?i)PREFIX){1}\s*([a-zA-Z]*:)\s*(<http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+#?>)\s*(\.?)\s*")
    lines = query.split('\n')
    lst = []
    for line in lines:
        subpatterns = re.split(pattern, line)
        # [0] '' [1] # [2] @prefix  [3] prefix [4] namespace [5] '.' [6] '' 
        if len(subpatterns) != 7 or subpatterns[1] == '#': continue
        if len(subpatterns[2] + subpatterns[5]) != 6: continue # false prefix format: PREFIX. or @prefix
        prefix, namespace = subpatterns[3][:-1], subpatterns[4][1:-1] #remove :, remove <>
        lst.append((prefix if prefix else ':' , namespace))
    return lst # [0] prefix [1] ns