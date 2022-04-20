import rdflib


def remove_all_namespaces(g: rdflib.Graph):
        #TODO create unbind method for graph
        g.namespace_manager.store._Memory__namespace = {}
        g.namespace_manager.store._Memory__prefix = {}