import json

from neo4j import GraphDatabase
from rdflib import Graph
import traceback
from sentence_transformers import SentenceTransformer
from vocabs.backend.neo4voc.query import CreateNode

def load_skos_embeddings(path, prefix, uri, lang='es',
                         model_name='sentence-transformers/all-MiniLM-L12-v2',
                         batch_size=100,
                         batch_n=1):
    """retorna todos los conceptos y sus ancestros del path


    esta consulta sparql retorna una lista, cada elemento contiene una lista con 6 elementos
    posiciones |  significado
    0          |  URI del concepto
    1          |  concept Label
    2          |  URI del grupo que calsifica al concepto
    3          |  group Label
    4          |  URI del dominio que calsifica al grupo
    5          |  domain Label

    """

    print("load model")
    model = SentenceTransformer(model_name)
    print("=====")


    print("query graph")
    g = Graph()
    g.parse(path)

    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX isothes: <http://purl.org/iso25964/skos-thes#>
    PREFIX {prefix}: {uri}
    SELECT DISTINCT  ?concept ?conceptLabel ?group ?groupLabel ?domain ?domainLabel
    WHERE {{
      # obtiene los dominios de la ontologia
      ?domain a {prefix}:Domain .
      # de esos dominios obtener sus miembros que en este caso son las agrupaciones intermedias
      ?domain skos:member ?group .
      # esos miembros son clasificados como ConceptGroup
      ?group a isothes:ConceptGroup  .
      # de esos grupos obtener sus miembros que son los conceptos
      ?group skos:member ?concept .
      # comprobar que son conceptos
      ?concept a skos:Concept .
    
      # obtener la propiedad Label de los dominios y filtrar por el español
      ?domain skos:prefLabel ?domainLabel
      FILTER(LANGMATCHES(LANG(?domainLabel), "{lang}"))
      # obtener la propiedad Label de los grupos y filtrar por el español
      ?group skos:prefLabel ?groupLabel
      FILTER(LANGMATCHES(LANG(?groupLabel), "{lang}"))
      # obtener la propiedad Label de los conceptos y filtrar por el español
      ?concept skos:prefLabel ?conceptLabel
      FILTER(LANGMATCHES(LANG(?conceptLabel), "{lang}"))
    
      }}
      """.format(prefix=prefix, uri=uri, lang=lang)
    print("=====")

    qres = g.query(query)

    errors = []
    concepts = []

    for row in qres:

        print("create emb")
        emb = model.encode(
                f'''El concepto {row[1]} está relacionado a  {row[3]}, {row[5]}''')
        c = {
            'str': "El concepto " + row[1] + " está relacionado a " + row[3] + ", " + row[5],
            'conceptUri': row[0].toPython(),
            'conceptLabel': row[1],
            # 'belongsTo': [
            #     {
            #         'grouppp': {
            #             'uri': row[2].toPython(),
            #             'label': row[3]
            #             },
            #         'domain': {
            #             'uri': row[4].toPython(),
            #             'label': row[5]
            #             }
            #         }
            #     ],
            'embedding': emb
            }
        print(c)

        concepts.append(c)
        try:
            node = CreateNode()
            node.build(identifier={'conceptUri': row[0].toPython()},
                       properties=c,
                       labels="Vocab:Concept")
            node.execute()
        except  Exception :
            errors.append({'error': traceback.format_exc(), 'concept':c})

    with open('data/errors.json', 'w', encoding='utf-8') as f:
        json.dump(errors, f, ensure_ascii=False, indent=4)

    return concepts
#
#
# def neo4j():
#     URI = 'bolt://localhost:7687'
#     AUTH = ('neo4j', '1qazxsw2')
#     DB_NAME = 'vocs'
#
#     driver = GraphDatabase.driver(URI, auth=AUTH, encrypted=True)
#     driver.verify_connectivity(database=DB_NAME)
#
#     with driver.session(database=DB_NAME) as session:
#

# neo4j()

concepts = load_skos_embeddings("data/unesco-thesaurus.ttl", "unesco",
                 "<http://vocabularies.unesco.org/ontology#>", lang='es')
# print(concepts)
