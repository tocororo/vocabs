from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_neo4j import Neo4jVector
from langchain_neo4j.vectorstores.neo4j_vector import DEFAULT_SEARCH_TYPE

from vocabs.backend.neo4voc.connection import Connection, NEO4J_DRIVER_HOST, NEO4J_USERNAME, NEO4J_PASSWORD

# This is a sentence-transformers model: 
# It maps sentences & paragraphs to a 384 dimensional dense vector space
# and can be used for tasks like clustering or semantic search.
# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
# model                                     dimensional dense vector
# sentence-transformers/all-mpnet-bembeddingsase-v2     768
# sentence-transformers/all-MiniLM-L12-v2               384
# sentence-transformers/all-MiniLM-L6-v2                384 (have the best results in the example)


class Vector(object):

    # itself instance, following with Singleton desing pattern
    instance = None
    
    __neo_vector:Neo4jVector

    def __new__(cls):
        """ it is a private function that create if not exists a `Vector` instance """

        if cls.instance is None:
            cls.instance = object.__new__(cls)
            cls.__init(cls)

        return cls.instance
    
    def __init(self):
        self.__neo_vector = None

    def create_neo_index(self,
            vector_name, 
            node_labels,
            property_to_save_embedding= 'embedding', 
            vector_dimension= 768, 
            similarity_function='cosine'):
        c = Connection()
        # "CREATE VECTOR INDEX unesco_manual12 IF NOT EXISTS FOR (n:Unesco) ON (n.unesco_manual12) OPTIONS { indexConfig:{ `vector.dimensions`: 768, `vector.similarity_function`: 'cosine', `vector.quantization.enabled`: false, `vector.hnsw.m`: 16, `vector.hnsw.ef_construction`: 100 } }")
        return c.query("CREATE VECTOR INDEX "+vector_name+" IF NOT EXISTS \
            FOR (n:"+node_labels+") \
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

    def set_node_properties(self, label, property_name, lang:str = 'es', split_separator='@'):
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

    def create_neo_index_from_graph(self,
            vector_name:str= 'index', 
            node_label:str= "Unesco",
            text_node_properties=[],
            embedding_property_saved:str= 'embedding', 
            embeddings:Embeddings= None
            ):
        """"""
        c = Connection()
        self.__neo_vector = Neo4jVector.from_existing_graph(
                        embedding= embeddings, 
                        url= c.uri(),
                        username= NEO4J_USERNAME,
                        password= NEO4J_PASSWORD,
                        embedding_node_property= embedding_property_saved, 
                        index_name= vector_name,
                        node_label= node_label,
                        text_node_properties=text_node_properties
                        )
        return self.__neo_vector

    def access_neo_index(self, index_name:str, query:str, k=5):
        c = Connection()
        # get the index
        print('index_name=',index_name)
        records, s, keys= c.query("show index YIELD name, type, properties WHERE type='VECTOR' and lower(name)=lower('"+index_name+"') RETURN name, properties")
        # rebuild the embedding model name from index property
        # remove the language, example from `_es_all_MiniLM_L6_v2` remove `_es_`
        pre_name= str(records[0]['properties'][0])
        print('pre_name=', pre_name)
        # It is important to save the actual database index name because we adapt the name to a better user interface.
        index_name_from_DB= str(records[0]['name'])
        print('index_name_from_DB=',index_name_from_DB)
        language= ''
        for lang in ['es','en']:
            if ('_'+lang+'_') in pre_name:
                pre_name= pre_name.split('_'+lang+'_')[1]
                language = lang
        # # remove the index name, example from `unesco_es_all_MiniLM_L6_v2` remove `unesco`
        # pre_name = str(records[0]['properties'][0]).lower().removeprefix(index_name)
        print('pre_name_whitout_lang=', pre_name)
        # finally replace `_` for `-`
        name = pre_name.replace('_','-')

        model_name = 'sentence-transformers/' + name
        print('model_name', model_name)
        embeddings_provider = HuggingFaceEmbeddings(model_name= model_name)
        self.index= Neo4jVector.from_existing_index(
                                    embedding=embeddings_provider,
                                    index_name=index_name_from_DB,
                                    url= c.uri(),
                                    username= NEO4J_USERNAME,
                                    password= NEO4J_PASSWORD,
                                    search_type= DEFAULT_SEARCH_TYPE
                                )
        self.index.text_node_property = '_prefLabel_'+ language
        print('query=',query)
        return self.index.similarity_search_with_score(query=query,k=k)

    def similar_from_index(self, query,k=5):
        return self.index.similarity_search_with_score(query=query,k=k)
    
    def get_index_names(self)->list:
        """Gets the list of index names"""
        c= Connection()
        records, summary, keys= c.query("show index YIELD name, type WHERE type='VECTOR' RETURN name")
        return records
    
    def get_indexes(self):
        c = Connection()
        return c.query("SHOW VECTOR INDEXES yield *")
    
class Index:
    
    
    index_name_from_DB: str

    labelsOrTypes_from_DB: list[str]

    properties_from_DB: list[str]


    name_for_user: str

    node_property: str

    model_name: str

    lang: str

    lang_separator: str = '@'

    __lang_list: list

    node_label: str

    vector_dimension: int

    similarity_function: str


    def __init__(self):
        self.name_for_user = ''
        self.node_property = self.get_node_property()
        self.model_name = self.get_model_name()

    

