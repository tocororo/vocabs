from rdflib import Graph
from rdflib_neo4j import Neo4jStore, Neo4jStoreConfig, HANDLE_VOCAB_URI_STRATEGY, HANDLE_MULTIVAL_STRATEGY
from vocabs.backend.neo4voc.connection import Connection, NEO4J_DRIVER_DB, NEO4J_DRIVER_HOST, NEO4J_USERNAME, NEO4J_PASSWORD
from vocabs.frontend.locales.languaje import _

class NeoSemantics():
    
    def create_constraint(self):
        '''
            This function will create a constraint to make the `uri` property of all nodes tagged as `Resource` unique.
        '''
        connection = Connection()
        records, summary, keys = connection.query('SHOW CONSTRAINTS')
        for record in records:
            if record['name'] == 'n10s_unique_uri':
                raise Exception(_('The constraint already exists'))

        return connection.query('CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource) REQUIRE r.uri IS UNIQUE;')
        
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
            raise Exception(_("Parameter 'path' must be given."))
        path = kwargs['path']
        format = ''
        if 'format' not in kwargs:
            raise Exception(_("Parameter 'format' must be given."))
        format = kwargs['format']
        if 'tags' not in kwargs:
            raise Exception(_("Parameter 'tags' must be given."))
        tags:dict = kwargs['tags']
        if 'identifier' not in tags:
            raise Exception(_("Parameter 'tags' must have a property 'identifier'."))
        if 'id_value' not in tags:
            raise Exception(_("Parameter 'tags' must have a property 'id_value'."))
        if 'labels' not in tags:
            raise Exception(_("Parameter 'tags' must have a property 'labels'."))

        auth_data = {'uri': "bolt://" + NEO4J_DRIVER_HOST + ":7687",
             'database': NEO4J_DRIVER_DB,
             'user': NEO4J_USERNAME,
             'pwd': NEO4J_PASSWORD}
        config = Neo4jStoreConfig(auth_data=auth_data,
                          handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.MAP,
                          handle_multival_strategy=HANDLE_MULTIVAL_STRATEGY.ARRAY,
                          batching=True)

        # Create the RDF Graph, parse & ingest the data to Neo4j, and close the store(If the field batching is set to True in the Neo4jStoreConfig, remember to close the store to prevent the loss of any uncommitted records.)
        neo4j_graph = Graph(store=Neo4jStore(config=config))
        # Calling the parse method will implictly open the store
        neo4j_graph.parse(path, format=format)  #formats: ttl, xml
        # Close the connection and save the data
        neo4j_graph.close(True)

        #uri: http://aims.fao.org/aos/agrovoc
        self.add_labels_to_nodes(property=tags['identifier'], property_value=tags['ide_value'], labels=tags['labels'])

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
            raise Exception(_("Parameter 'property' must be given."))
        property = kwargs['property']

        if 'property_value' not in kwargs:
            raise Exception(_("Parameter 'property_value' must be given."))
        property_value = kwargs['property_value']
        
        if 'labels' not in kwargs:
            raise Exception(_("Parameter 'labels' must be given."))
        labels = kwargs['labels']

        connection = Connection()
        # MATCH (n:Unesco) RETURN count(n) as count
        connection.query('MATCH (n) WHERE n.'+property+' CONTAINS "'+property_value+'" SET n:'+labels+' RETURN n')