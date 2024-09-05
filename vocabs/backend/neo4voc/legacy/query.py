# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from iroko_graph.connection import Connection



UNDIRECTED = '-'
DIRECTED = '->'


class Query:

    query: str = None

    __connection: Connection


    def __init__(self):
        self.query = ''
        self.__connection = Connection()


    def execute(self):
        """
            Executes the query built.
        """
        self.__connection = Connection()
        self.__connection.create(self.query)


    def dict_to_cypher(self, properties: dict) -> str:
        """ 
            converts `dict` in `cypher` string.\n
            Example:\n
            `dict` :  { 'name' : 'Martha'}\n
            `cypher` : { name : 'Martha'}
        """
        cypher = '{'
        pos = 0
        for k, v in properties.items():
            cypher += k + ":'" + str(v) + "'"
            if pos < len(properties) - 1:
                cypher += ","
            pos += 1
        return cypher + "}"


    def dict_to_cypher_object_properties(self, properties: dict, object_name='n') -> str:
        """
            converts `dict` in `cypher_object` string.\n
            Example:\n
            `dict` :  { 'name' : 'Martha'}\n
            `cypher_object` : n.name= 'Martha',
        """
        cypher = ''
        pos = 0
        for k, v in properties.items():
            # TODO: if the vale of `v` is a dict then is a problem, this will need a solution...
            if type(v) is str and str(v).find("{") != -1 and str(v).find("}") != -1 :
                # that means `v` have a `dict` so replaces ' by "
                r = ''
                for i in v:
                    if i is "'":
                        r += '"'
                    else: r += i
                v = r
                print('is a str-----', v)
            cypher += object_name + '.' + k + "='" + str(v) + "'"
            if pos < len(properties) - 1:
                cypher += ","
            pos += 1
        return cypher 



class CreateNode(Query):
    """ Builds a cypher query for create or update a `Node` in Neo4j data base """
    
    def __init__(self):
        super(CreateNode,self)


    def build(self, **kwargs) -> str:
        """
            Builds a query for create or update `Node`.\n
            `identifier` : is a `dict`, represents a property or more to identify a `node`.\n
            `properties` : is a `dict`, represents all properties of a `node`.\n
            `labels` : is a `str` can be a word or if has more that ones must be with this structure `label1:label2:label3 ...`
            which recommended style are camel case, beginning with an upper-case character. Example  'VehicleOwner'\n

            Example: \n
                MERGE (n:Person {name: "Martha"})
                ON MATCH SET n.age= 54, n.last_updated = timestamp()
                ON CREATE SET n.age= 54, n.craeted = timestamp();
        """

        labels = ''
        if 'labels' in kwargs:
            labels = kwargs['labels']

        properties = ''
        if 'properties' in kwargs:
            properties = self.dict_to_cypher_object_properties(kwargs['properties'])
            properties += ','

        identifier = ''
        if 'identifier' not in kwargs:
            raise Exception("Parameter 'identifier' must be given. Otherwise the graph will corrupt ")
        else:
            identifier = self.dict_to_cypher(kwargs['identifier'])


        self.query = str( 
            "MERGE (n:" + labels + " " + identifier + ") \
             ON MATCH SET  " + properties + " n.updated_at = timestamp() \
             ON CREATE SET " + properties + " n.craeted_at = timestamp() \
            RETURN n"
        )

        return self.query



class CreateRelationship(Query):
    """ Builds a cypher query for create a `Relationship` between two `Nodes` in Neo4j data base """

    def __init__(self):
        super(CreateRelationship,self)


    def build(self, **kwargs) -> str:
        """
            Builds a query for create or update a `Relationship`.\n
            The function needs two nodes (source and target) to make a relation between them;
            also needs a direction to establish if it will be directional or not

            `nodes` : is a `[]` with two elements, must be given.
                Each elemet is a `dict` with his identifier properties and labels.
                Example: 
                    [
                        {
                            'labels': 'Person', #### not required
                            'identifier': { 'name': 'Martha'} #### REQUIRED
                        },
                        {
                            'labels': 'Town',
                            'identifier':{ 'name': 'Celso Maragoto'}
                        }
                    ]

            `label` : is a `str`, can be a word which recommended style are upper-case character. Example  'LIVE_IN'

            `properties` : is a `dict`, represents all properties of a relationship.\n

            `direction` : is a `str` by default is an undirected relationship

            Example:\n
                MATCH (n:Person { name: 'Matha' }),(t:Town { name: 'Celso Maragoto' })
                MERGE (n)-[r:LIVE_IN ]->(t)
                ON MATCH SET  r.from= '10-01-2000', r.updated_at = timestamp()
                ON CREATE SET r.from= '10-01-2000', r.craeted_at = timestamp()
                RETURN *
        """

        nodes = list()
        if 'nodes' not in kwargs:
            raise Exception("Parameter 'nodes' must be given. Otherwise the graph will corrupt ")

        elif len(kwargs['nodes']) < 2:
            raise Exception("Parameter 'nodes' must be two elements. Otherwise the graph will corrupt ")

        else:
            for node in kwargs['nodes']:
                labels = str()
                if 'labels' in node:
                    labels = ':' + node['labels']

                if 'identifier' not in node:
                    raise Exception("One element in parameter 'nodes' must be called identifier and is a `dict` with node identifiers. Otherwise the graph will corrupt ")

                identifier = self.dict_to_cypher(node['identifier'])
                nodes.append(dict(labels= labels, identifier= identifier))

        properties = str()
        if 'properties' in kwargs:
            properties = self.dict_to_cypher_object_properties(kwargs['properties'], object_name='r')
            properties += ','

        relationship_label = str()
        if 'label' in kwargs:
            relationship_label = kwargs['label']

        direction = UNDIRECTED
        if 'direction' in kwargs:
            direction = kwargs['direction']

        self.query = str( 
            "MATCH (n1" + nodes[0]['labels'] + " " + nodes[0]['identifier'] + "), (n2" + nodes[1]['labels'] + " " + nodes[1]['identifier'] + ") \
             MERGE (n1)-[r:" + relationship_label + "]"+ direction +"(n2) \
             ON MATCH SET  " + properties + " r.updated_at = timestamp() \
             ON CREATE SET " + properties + " r.craeted_at = timestamp() \
            RETURN *"
        )

        return self.query


class CreateMatch(Query):
    """ Builds a cypher query to select any `Node` in Neo4j data base """

    __match = 'MATCH'
    __with = 'WITH'
    __where = 'WHERE'
    __return = 'RETURN'
    
    def __init__(self):
        super(CreateMatch,self)


    def build(self, dictionary: dict):#labels: str, properties: dict):
        """
            Builds a query to select any `Node`.\n

            `properties` : is a `dict`, represents all properties of a node.\n

            `labels` : is a `str` can be a word or if has more that ones must be with this structure `label1:label2:label3 ...`\n
            which recommended style are camel case, beginning with an upper-case character. Example  'VehicleOwner'

            `aggregations` : 

            `where` : { propertyName : "operator posible_value", ... }
            if `where` condition have more that ones, then can include operators as properties like this:
                where : { propertyName : "operator posible_value", and: '', otherProperty: 'other_operator other_posible_value', ... }



            { 
                'match': { 
            
                    'variable': 'jhon', 
            
                    'properties' : { 'name': 'Jhon', 'age': '20' }, 
            
                    'labels' : ':Person:Male', 
            
                    'relations': [
                        {
                            'label': ':FRIEND',
                            'variable': '',
                            direction : '' ### can be  ''|'left'|'rigth' 
                        },
                        {
                            'label': ':FRIEND',
                            'variable': 'fof',
                            direction : 'left'
                        },
                    ]
                }, 
                'where' : {  
            
                    'dni': 'is 93043932', 
            
                    'or': '', 
            
                    'dni': "STARTS WITH '91'" 
            
                }, 
            
                'return': [ 
                    { 
                        'variable': 'jhon', 
                        'properties': [ 'name' ], 
                        'aggregations': {  
                            'count': '' 
                        },    ### other example can be  { count: 'DISTINCT name' }  
            
                    }, 
                    { 
                        'variable': 'fof', 
                        'properties': ['name'] 
                    } 
                ] 
            
            }
        """

        self.query = str("Match (n) RETURN n")

        self._build_match(dictionary)



        return self.query




    def _build_match(self, param: dict):
        """
            'match': {

                    'variable': 'jhon',

                    'properties' : { 'name': 'Jhon', 'age': '20' },

                    'labels' : ':Person:Male',

                    'relations': [
                        {
                            'label': ':FRIEND',
                            'variable': '',
                            direction : '' ### can be  ''|'left'|'rigth' 
                        },
                        {
                            'label': ':FRIEND',
                            'variable': 'fof',
                            direction : 'left'
                        },
                    ]
                }
            
            { 'match': { 
                'variable': 'charlie', 
                'properties': { 
                    'name': 'Charlie Sheen'
                    }, 
                'relations': [ 
                    { 'label': ':ACTED_IN', 'variable': 'movie', 'direction':'rigth'}, 
                    {'label':':DIRECTED', 'variable':'director', 'direction':'left'}
                    ]
                }
            }
            MATCH (charlie { name: 'Charlie Sheen' })-[:ACTED_IN]->(movie)<-[:DIRECTED]-(director)

        """

        if 'match' not in param:
            raise Exception("Can not build a 'Match' query. Missing arguments")

        match = param['match']

        self.__match = "MATCH ("

        if 'variable' in match:
            self.__match += match['variable']

        if 'labels' in match:
            self.__match += match['labels']

        if 'properties' in match:
            self.__match += ' ' + self.dict_to_cypher(match['properties'])

        self.__match += ')'

        if 'relations' in match:

            for relation in match['relations']:

                if relation['direction'] == '':
                    self.__match += '-[' + relation['label'] + ']-(' + relation['variable'] +')'

                elif relation['direction'] == 'left':
                    self.__match += '<-[' + relation['label'] + ']-(' + relation['variable'] +')'

                elif relation['direction'] == 'rigth':
                    self.__match += '-[' + relation['label'] + ']->(' + relation['variable'] +')'

        print(self.__match)

        return self.__match


    def _build_return(self, param: dict):
        """
            'return': [ 
                { 
                    'variable': {
                        'var': 'jhon', 
                        'properties': [ 'name' ],
                    },
                    'aggregations': {  
                        'count': '' 
                    },    ### other example can be  { count: 'DISTINCT name' }  
        
                }, 
                { 
                    'variable': 'fof', 
                    'properties': ['name'] 
                } 
            ] 
        """

        self.__return = "RETURN * "








