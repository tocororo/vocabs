# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

""" Aplication Interface """

from flask import current_app

from neo4j import GraphDatabase, basic_auth, Driver

class Connection(object):
    """
        Implements two design patterns, Facade and Singleton to create a unique instance and an interface between this module and Neo4j module.
        Class that gives a connection and the basic operations with Neo4j data base.

            load from current app config 3 values: \n
            `IROKO_GRAPH_NEO4J_DRIVER_HOST` : IP direction or URL\n
            `IROKO_GRAPH_NEO4J_USERNAME` : User name with privilages in Neo4j data base\n
            `IROKO_GRAPH_NEO4J_PASSWORD` : Password to auth
    """
    # itself instance, following with Singleton desing pattern
    instance = None

    # driver of connection
    __driver : Driver = None

    def __new__(cls):
        """ it is a private function that create if not exists a `Connection` instance """

        if cls.instance is None:
            cls.instance = object.__new__(cls)
            cls.__init(cls)

        return cls.instance

    def __init(self):
        """
            It is a private function that opens a connection with Neo4j data base.
            Loads from current app config 3 values: \n
            `IROKO_GRAPH_NEO4J_DRIVER_HOST` : IP address or URL\n
            `IROKO_GRAPH_NEO4J_USERNAME` : User name with privilages in Neo4j data base\n
            `IROKO_GRAPH_NEO4J_PASSWORD` : Password to auth
        """

        if not current_app.config['IROKO_GRAPH_NEO4J_DRIVER_HOST'] or not current_app.config['IROKO_GRAPH_NEO4J_USERNAME'] or not current_app.config['IROKO_GRAPH_NEO4J_PASSWORD'] :
            raise Exception("missing arguments to set up a connection with Neo4j data base")

        uri = "bolt://" + current_app.config['IROKO_GRAPH_NEO4J_DRIVER_HOST'] + ":7687"
        username = current_app.config['IROKO_GRAPH_NEO4J_USERNAME']
        password = current_app.config['IROKO_GRAPH_NEO4J_PASSWORD']

        self.__driver = GraphDatabase.driver( uri, auth=basic_auth( username, password), encrypted=True)

        print("connection established!!!")


    def close(self):
        """ Closes the connection with Neo4j data base """
        self.__driver.close()


    def query(self, query: str):
        """ Executes a query and returns the result. """
        with self.__driver.session() as session:
            results = session.run(query)
            return results


    def create(self, query: str):
        """ Executes a `create` query and returns the result. This function also makes a commit into data base. """
        with self.__driver.session() as session:
            transaction = session.begin_transaction()
            n = transaction.run( query ).single().value()
            transaction.commit()
            return n


    def database_all_info(self):
        """ Returns the graph """
        with self.__driver.session() as session:
            results = session.run('MATCH(n) RETURN n;')
            for record in results:
                print(record)



class Node:
    """
        Represents a `node` entity in Neo4j data base.\n

        `label` is a `str` field which recommended style are camel case, beginning with an upper-case character. Example  ':VehicleOwner'\n
        if has more that ones must be with this structure `label1:label2:label3 ...`\n

        `properties` is a `dict` which keys are named lower camel case, beginning with a lower-case character. Example 'firstName'
    """

    __schema: dict = None

    __properties: dict = None

    __labels : str

    def __init__(self):
        self.__schema = dict()
        self.__properties = dict()
        self.__labels = ''


    @property
    def schema(self):
        return self.__schema

    @schema.setter
    def schema(self, value):
        self.__schema = value


    @property
    def properties(self):
        return self.__properties

    @properties.setter
    def properties(self, value):
        self.__properties = value

    @property
    def labels(self) -> str:
        """
            `labels`: is used to shape the domain by grouping nodes into sets,\n
                where all nodes that have a certain label belongs to the same set.\n
                if has more that ones must be with this structure `label1:label2:label3 ...`
        """
        return self.__labels

    @labels.setter
    def labels(self, value):
        """
            `labels`: is used to shape the domain by grouping nodes into sets,\n
                where all nodes that have a certain label belongs to the same set.\n
                if has more that ones must be with this structure `label1:label2:label3 ...`
        """
        self.__labels = value

    def _to_cypher(self):
        """ convert `dict` in `cypher` string. """
        cypher = '{'
        pos = 0
        for k, v in self.__properties.items():
            cypher += k + ":'" + v + "'"
            if pos < len(self.__properties) - 1:
                cypher += ","
            pos += 1
        return cypher + "}"


class Graph:
    """  """

    #  May be don't needed!!!
    __node = None


    __connection: Connection = None



    def __init__(self):
        self.__node_schema = dict()
        self.__connection = Connection()


    def push_node(self, node: Node):
        """
            Create a `Node` in data base.\n
            `node` : is a `Node` object
        """

        query = str("CREATE (n:" + node.labels + " " + node._str_to_cypher() + ") RETURN n")
        result = self.__connection.create(query)
        return result


    def match(self, labels: str):
        """ excecute a `MATCH` query filtering by labels """
        query = str("MATCH (n: " + labels + ") RETURN n")
        return self.__connection.query(query)

    def match_by_properties(self, properties: dict):
        """ excecute a `MATCH` query filtering by labels """
        node = Node()
        node.properties = properties
        query = str("MATCH (n: " + node._to_cypher() + ") RETURN n")
        return self.__connection.query(query)
