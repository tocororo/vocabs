from decimal import Decimal
from rdflib import RDF, Graph, Literal
from rdflib_neo4j import Neo4jStore, Neo4jStoreConfig, HANDLE_VOCAB_URI_STRATEGY, HANDLE_MULTIVAL_STRATEGY
from rdflib_neo4j.Neo4jTriple import Neo4jTriple
from vocabs.backend.neo4voc.connection import Connection, NEO4J_DRIVER_DB, NEO4J_DRIVER_HOST, NEO4J_USERNAME, NEO4J_PASSWORD
from vocabs.frontend.locales.language import Language

def parse_triple(self, triple, mappings):
    """
    Parses a triple and updates the Neo4jTriple object accordingly.

    Args:
        triple: The triple to parse.
        mappings: A dictionary of mappings for predicate URIs.
    """
    (subject, predicate, object) = triple

    # Getting a property
    if isinstance(object, Literal):
        # Neo4j Python driver does not support decimal params
        value = float(object.toPython()) if type(object.toPython()) == Decimal else object.toPython()
        prop_name = self.handle_vocab_uri(mappings, predicate)
        
        # If at least a name is defined and the predicate is one of the properties defined by the user
        if self.handle_multival_strategy == HANDLE_MULTIVAL_STRATEGY.ARRAY and \
                str(predicate) in self.multival_props_names:
            if object.language is not None:
                value = object.value + '@' + object.language
            self.add_prop(prop_name, value, True)
        # If the user doesn't define any predicate to manage as an array, then everything is an array
        elif self.handle_multival_strategy == HANDLE_MULTIVAL_STRATEGY.ARRAY and not self.multival_props_names:
            if object.language is not None:
                value = object.value + '@' + object.language
            self.add_prop(prop_name, value, True)
        else:
            self.add_prop(prop_name, value)

    # Getting a label
    elif predicate == RDF.type:
        self.add_label(self.handle_vocab_uri(mappings, object))

    # Getting its relationships
    else:
        rel_type = self.handle_vocab_uri(mappings, predicate)
        self.add_rel(rel_type, object)

class NeoSemantics():
    # ********************************
    # creates the variable `_` that contains the translation documents.
    # ********************************
    _ = None
    strategy = None
    multival_strategy = None
    def __init__(self):
        l = Language()
        self._ = l.language()
        self.strategy = HANDLE_VOCAB_URI_STRATEGY.MAP 
        self.multival_strategy = HANDLE_MULTIVAL_STRATEGY.ARRAY
        # The following line overwrites the function `parse_triple` of the library `rdflib_neo4j` 
        # because it dose not consider the language property of the `Literal` object  
        Neo4jTriple.parse_triple = parse_triple
    
    def create_constraint_and_default_config(self):
        '''
            This function will create a constraint to make the `uri` property of all nodes tagged as `Resource` unique.
            This step assumes that the neosemantics plugin is installed in neo4j, otherwise the configuration will fail.
        '''
        connection = Connection()
        records, summary, keys = connection.query('SHOW CONSTRAINTS')
        constraint = None
        for record in records:
            if record['name'] != 'n10s_unique_uri':
                constraint = connection.query('CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource) REQUIRE r.uri IS UNIQUE;')
                # raise Exception(self._('The constraint already exists'))

        records, summary, keys = connection.query('call n10s.graphconfig.show')
        config = None
        if records == []:
            config = connection.query("CALL n10s.graphconfig.init({ \
                                        handleVocabUris: '"+ self.strategy.value +"', \
                                        handleMultival: '"+ self.multival_strategy.name +"', \
                                        keepLangTag: true, \
                                        keepCustomDataTypes: true, \
                                        applyNeo4jNaming: true \
                                    });")
        
        return config, constraint 
        
    def import_data_n10s(self, **kwargs):
        path = ''
        if 'path' not in kwargs:
            raise Exception(self._("Parameter 'path' must be given."))
        path = kwargs['path']
        format = ''
        if 'format' not in kwargs:
            raise Exception(self._("Parameter 'format' must be given."))
        format = kwargs['format']
        c = Connection()
        return c.query("CALL n10s.rdf.import.fetch( \
                '"+path+"', \
                '"+format+"' \
                )")


    def import_data(self, **kwargs):
        '''
            Import RDFs to Neo4j\n
            @Parameters:\n 
            `path`: URL or local file where the RDF file is located\n
            `format`: Must be `ttl` for turtle files or `xml` for RDF/XML files
            `tags`: Is a dict that have three properties, \n
            ------`identifier`, is a `str`, is the name of the property\n
            ------`id_value`, is a `str`, is the value of the identifier\n
            ------`labels`, is a `str`, can be a word or if has more that ones must be with this structure `label1:label2:label3 ...`\n
            tags= {
                'identifier': 'uri',
                'id_value': 'vocabularies.unesco.org',
                'labels': 'Unesco'
            }
        '''
        path = ''
        if 'path' not in kwargs:
            raise Exception(self._("Parameter 'path' must be given."))
        path = kwargs['path']
        format = ''
        if 'format' not in kwargs:
            raise Exception(self._("Parameter 'format' must be given."))
        format = kwargs['format']
        if 'tags' not in kwargs:
            raise Exception(self._("Parameter 'tags' must be given."))
        tags:dict = kwargs['tags']
        if 'identifier' not in tags:
            raise Exception(self._("Parameter 'tags' must have a property 'identifier'."))
        if 'id_value' not in tags:
            raise Exception(self._("Parameter 'tags' must have a property 'id_value'."))
        if 'labels' not in tags:
            raise Exception(self._("Parameter 'tags' must have a property 'labels'."))

        auth_data = {'uri': "bolt://" + NEO4J_DRIVER_HOST + ":7687",
             'database': NEO4J_DRIVER_DB,
             'user': NEO4J_USERNAME,
             'pwd': NEO4J_PASSWORD}
        config = Neo4jStoreConfig(auth_data=auth_data,
                          handle_vocab_uri_strategy= self.strategy,
                          handle_multival_strategy= self.multival_strategy,
                          multival_props_names=[
                              ("skos","prefLabel"), 
                              ("skos","altLabel"), 
                              ('dct','description'), 
                              ('dct','title'), 
                              ('skosxl','literalForm'), 
                              ('skos','scopeNote')],
                          batching=True)

        # Create the RDF Graph, parse & ingest the data to Neo4j, and close the store(If the field batching is set to True in the Neo4jStoreConfig, remember to close the store to prevent the loss of any uncommitted records.)
        neo4j_graph = Graph(store=Neo4jStore(config=config))
        # Calling the parse method will implictly open the store
        neo4j_graph.parse(path, format=format)  #formats: ttl, xml
        # Close the connection and save the data
        neo4j_graph.close(True)

        #uri: http://aims.fao.org/aos/agrovoc
        self.add_labels_to_nodes(property=tags['identifier'], property_value=tags['id_value'], labels=tags['labels'])

    def add_labels_to_nodes(self, **kwargs):
        """
            Adds labels to nodes that contain a certain value in a specified property, it does not remove labels that it already has\n
            @Parameters:\n
            `property` is a `str`, is the name of the property by which the search criteria will be established \n
            `property_value` is a `str`, is the value by which the search will be performed, this value does not have to be a complete string because `CONTAINS` is being used \n
            `labels` : is a `str`, can be a word or if has more that ones must be with this structure `label1:label2:label3 ...`
            which recommended style are camel case, beginning with an upper-case character. Example  'VehicleOwner'\n

            @Example:\n
            property= 'uri'\n
            property_value= 'vocabularies.unesco.org'\n
            labels= 'Unesco'\n
            MATCH (n) WHERE n.uri CONTAINS "vocabularies.unesco.org" SET n:Unesco RETURN n
        """
        if 'property' not in kwargs:
            raise Exception(self._("Parameter 'property' must be given."))
        property = kwargs['property']

        if 'property_value' not in kwargs:
            raise Exception(self._("Parameter 'property_value' must be given."))
        property_value = kwargs['property_value']
        
        if 'labels' not in kwargs:
            raise Exception(self._("Parameter 'labels' must be given."))
        labels = kwargs['labels']

        connection = Connection()
        # MATCH (n:Unesco) RETURN count(n) as count
        connection.query('MATCH (n) WHERE n.'+property+' CONTAINS "'+property_value+'" SET n:'+labels+' RETURN n')