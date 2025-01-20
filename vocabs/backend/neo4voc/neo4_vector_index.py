from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_neo4j import Neo4jVector

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

def access_neo_index(
        vector_name:str= 'index', 
        node_label:str= "Unesco",
        text_node_properties=[],
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