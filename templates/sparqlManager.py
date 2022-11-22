import os
import rdflib
from typing import Dict, Union, Any
from utils import convert_color
class SparqlManager:
    def __init__(self) -> None:
        self.path = os.path.join(os.getcwd(), 'requests')

    def read_request(self, request_name: str) -> str:
        if not request_name.endswith('.rq'): request_name += '.rq'
        full_path = os.path.join(self.path, request_name)
        try:
            with open(full_path, 'r') as rq:
                return rq.read()
        except Exception as e:
            raise e

    def replace_placeholders(self, request: str, mapping: dict[str, str]):
        for k, v in mapping.items():
            request = request.replace(k,v)
        return request

    def convert_result_to_list(self, rst: rdflib.query.Result) -> list:
        l = list()
        for rst_row in rst:
            l.append(rst_row.asdict())
        return l

    def execute(self, request_name:str, g: rdflib.ConjunctiveGraph,  mapping: dict[str, str]) -> list:
        rq = self.read_request(request_name)
        rq = self.replace_placeholders(rq, mapping)
        rst = g.query(rq)
        return self.convert_result_to_list(rst)

    
    # Get objects from single list
    def get_list_items(self, g:rdflib.Graph, bn: rdflib.BNode, l=list()) -> list:
        next_bn = g.value(subject=bn, predicate=rdflib.RDF.rest)
        l.append(g.value(subject=bn, predicate=rdflib.RDF.first))
        if next_bn != rdflib.RDF.nil: 
            self.get_list_items(g, next_bn, l)
        return l


    def load_story_info(self, story: str, path: str = '') -> Dict[str, Union[str, Any]]:
        p = os.path.join(path, story) if path else story
        info_path   = os.path.join(p, 'info.ttl')
        people_path = os.path.join(p, 'db', 'people.ttl')
        g = rdflib.ConjunctiveGraph().parse(info_path).parse(people_path)

        info = self.execute('get_info', g, dict())[0]
        authors = self.execute('get_authors', g, dict())
        story_info = {
            'path': story,
            'title': info['title'].toPython(),
            'media_source': info['trailer'].toPython(),
            'authors': [author['author'].toPython() for author in authors],
            'tags': info['tags'].toPython().split(','),
            'desc': info['desc'].toPython()
        }
        colors = [list(map(float, info['bg'].__str__().split(','))), 
                list(map(float, info['fg'].__str__().split(','))),
                list(map(float, info['hl'].__str__().split(',')))
                ]
        story_info['colors'] = tuple(map(convert_color, colors))
        return story_info



