from dataclasses import replace
from sys import prefix
import rdflib
from rdflib import Dataset, Namespace, URIRef, ConjunctiveGraph
import os

from rdflib.namespace import FOAF


def unbind(g: rdflib.Graph, prefix: str):
    ns = g.namespace_manager.store._Memory__namespace[prefix]
    del g.namespace_manager.store._Memory__namespace[prefix]
    del g.namespace_manager.store._Memory__prefix[ns]
   
def clear_namespaces(g: rdflib.Graph):
    g.namespace_manager.store._Memory__namespace = {}
    g.namespace_manager.store._Memory__prefix = {}


#graph = ConjunctiveGraph()
#graph.get_context(URIRef('http://test/')
#).parse("http://www.w3.org/People/Berners-Lee/card.rdf")
#r = graph.query(querystr, loadContexts=True)



g = rdflib.Graph()

ds = ConjunctiveGraph()  #Dataset()

people = 'file:///' + os.path.abspath(os.path.dirname('stories/example/people.ttl')).replace('\\', '/') + '/'
print('people', people)
NS_PEOPLE = Namespace(people)


#clear_namespaces(g)

#g.parse('stories/example/locations.ttl')
#g.bind(prefix='loc', namespace=Namespace('file:///locomoto'))

#ds.get_context(URIRef('locations.ttl')).parse('stories/example/locations.ttl')

people: rdflib.Graph = ds.get_context(URIRef('people.ttl')).parse('stories/example/people.ttl', publicID=URIRef('File:///people.ttl'))
#loc = ds.get_context(URIRef('locations.ttl')).parse('stories/example/locations.ttl')
#print('loc', type(loc))
#g.base = PEOPLE
#people.bind('people', NS_PEOPLE)
#people.bind(prefix='foaf', namespace=NS_PEOPLE)


#loc.bind(prefix='loc', namespace=Namespace('file:///locomoto'), override=False, replace=True)

#g.bind(namespace=PEOPLE)
#ds.add_graph(g)

qr = """
SELECT ?s  FROM <file:///D:/python_projects/wiregraph/wiregraph/project/stories/example/people.ttl> FROM <file:///D:/python_projects/wiregraph/wiregraph/project/stories/example/locations.ttl> WHERE { ?s ?p ?o .}

"""

#g.namespace_manager.unbind('loc')

print(ds.serialize())
#for x in ds.get_context(URIRef('people.ttl')).namespace_manager.namespaces():
#    print(x)
#self.__prefix[namespace] = prefix
#self.__namespace[prefix] = namespace

#unbind(g, 'geo')
#unbind(g, 'rdfs1')
#unbind(g, 'loc')
#print(g.namespace_manager.store._Memory__namespace['loc'])


#print(g.serialize())

#t = ConjunctiveGraph()
#t.base = URIRef('test#')

#rst =  t.query(qr) #ds.query(qr)


#for row in rst:
#    print(row)