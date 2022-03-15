import os
import rdflib


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