from rdflib import Graph

from vocabs.backend.gstore import GstoreConnector


def load(path):
    IP = "127.0.0.1"
    Port = 9999
    httpType = "ghttp"
    username = "root"
    password = "123456"
    gc = GstoreConnector(IP, Port, username, password, http_type=httpType)

    g = Graph()
    g.parse(path)