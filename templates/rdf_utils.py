import rdflib
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