from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_neo4j import Neo4jVector
from neo4j.graph import Node

from vocabs.backend.neo4voc.connection import Connection, NEO4J_DRIVER_HOST, NEO4J_USERNAME, NEO4J_PASSWORD

# This is a sentence-transformers model: 
# It maps sentences & paragraphs to a 384 dimensional dense vector space
# and can be used for tasks like clustering or semantic search.
# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
# model                                     dimensional dense vector
# sentence-transformers/all-mpnet-bembeddingsase-v2     768
# sentence-transformers/all-MiniLM-L12-v2               384
# sentence-transformers/all-MiniLM-L6-v2                384 (have the best results in the example)


# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
neo_vector:Neo4jVector = None
def create_neo_index(
        vector_name, 
        property_to_save_embedding= 'embedding', 
        vector_dimension= 768, 
        similarity_function='cosine'):
    c = Connection()
    # "CREATE VECTOR INDEX unesco_manual12 IF NOT EXISTS FOR (n:Unesco) ON (n.unesco_manual12) OPTIONS { indexConfig:{ `vector.dimensions`: 768, `vector.similarity_function`: 'cosine', `vector.quantization.enabled`: false, `vector.hnsw.m`: 16, `vector.hnsw.ef_construction`: 100 } }")
    return c.query("CREATE VECTOR INDEX "+vector_name+" IF NOT EXISTS \
        FOR (n:Unesco) \
        ON (n."+property_to_save_embedding+") \
        OPTIONS { \
            indexConfig:{ \
                `vector.dimensions`: "+str(vector_dimension)+", \
                `vector.similarity_function`: '"+similarity_function+"', \
                `vector.quantization.enabled`: false, \
                `vector.hnsw.m`: 16, \
                `vector.hnsw.ef_construction`: 100 \
            } \
        }")
def split_property():
    # 1. obtener los nodos segun un label
    # 2. para cada nodo
    #   2.1 obtener el valor de la propiedad que se pase por parametro
    #   2.2 dividir la propiedad en valor e idioma
    # 3. retornar el valor en forma de arreglo con formato [{valor, lenguaje},...]
    pass

def set_node_properties(label, property_name, lang:str = 'es', split_separator='@'):
    """
        This function adds a property to each `Node` according to the language.\n
        NOTE: If the property exists, it will be deleted first and then recreated with the new value.\n
        For example, a node that has the property `titles` of type list and with the format `['value@lang',...]`
        will create an extra property with the format `_propertyName_languageValue`
        of the following node,\n
        `n.title= ["Python es asombroso@es", "Python is awesome@en",...]` \n
        we add the property,\n
        `n._title_es= "Python es asombroso"` \n
        or if the language is English,\n
        `n._title_en= "Python is awesome"`\n

    """
    c = Connection()
    c.query(
        "MATCH (n:"+ label +") WHERE n._"+ property_name +"_"+lang+" IS NOT NULL SET n._"+ property_name +"_"+lang+"=null RETURN n"
    )

    records = c.query(
       "MATCH (n:"+ label +") \
        UNWIND n."+ property_name +" AS property \
        WITH n, property \
        WHERE size(split(property, '"+split_separator+"')) > 1 AND split(property, '"+split_separator+"')[1] = '"+ lang +"' \
        FOREACH (ignored IN [1] | \
        SET n._"+ property_name +"_"+lang+" = split(property, '"+split_separator+"')[0] +', '+ COALESCE(n._"+ property_name +"_"+lang+",'')  ) \
        RETURN n"
    )
    return records

def access_neo_index(
        vector_name:str= 'index', 
        node_label:str= "Unesco",
        text_node_properties=[],
        text_node_properties_language='es',
        embedding_property_saved:str= 'embedding', 
        embeddings:Embeddings= None
        ):
    """"""
    c = Connection()
    neo_vector = Neo4jVector.from_existing_graph(
                    embedding= embeddings, 
                    url= c.uri(), 
                    username= NEO4J_USERNAME, 
                    password= NEO4J_PASSWORD,
                    embedding_node_property= embedding_property_saved, 
                    index_name= vector_name,
                    node_label= node_label,
                    text_node_properties=text_node_properties
                    )
    return neo_vector

def get_indexes():
    c = Connection()
    return c.query("SHOW VECTOR INDEXES yield *")