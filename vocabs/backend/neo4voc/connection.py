# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

""" Aplication Interface """

from neo4j import Driver, GraphDatabase, basic_auth

IROKO_GRAPH_NEO4J_USERNAME = 'neo4j'
"""Username value for the Neo4j data base."""

IROKO_GRAPH_NEO4J_PASSWORD = '1qazxsw2'
"""Password value for the Neo4j data base."""

IROKO_GRAPH_NEO4J_DRIVER_HOST = 'localhost'
"""Driver value for the Neo4j data base."""

IROKO_GRAPH_NEO4J_DRIVER_DB = 'vocs'
"""Driver value for the Neo4j data base."""


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
    __driver: Driver = None

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

        if (not IROKO_GRAPH_NEO4J_DRIVER_HOST or
                not IROKO_GRAPH_NEO4J_USERNAME or
                not IROKO_GRAPH_NEO4J_PASSWORD):
            raise Exception("missing arguments to set up a connection with Neo4j data base")

        uri = "bolt://" + IROKO_GRAPH_NEO4J_DRIVER_HOST + ":7687"
        username = IROKO_GRAPH_NEO4J_USERNAME
        password = IROKO_GRAPH_NEO4J_PASSWORD
        self.__driver = GraphDatabase.driver(uri, auth=(username, password),
                                             encrypted=False)

        print("connection established!!!")

    def close(self):
        """ Closes the connection with Neo4j data base """
        self.__driver.close()

    def query(self, query: str):
        """ Executes a query and returns the result. """
        with self.__driver.session(database=IROKO_GRAPH_NEO4J_DRIVER_DB) as session:
            results = session.run(query)
            return results

    def create(self, query: str):
        """ Executes a `create` query and returns the result.
        This function also makes a commit into data base. """
        with self.__driver.session(database=IROKO_GRAPH_NEO4J_DRIVER_DB) as session:
            transaction = session.begin_transaction()
            n = transaction.run(query).single().value()
            transaction.commit()
            return n

    def database_all_info(self):
        """ Returns the graph """
        with self.__driver.session(database=IROKO_GRAPH_NEO4J_DRIVER_DB) as session:
            results = session.run('MATCH(n) RETURN n;')
            for record in results:
                print(record)

