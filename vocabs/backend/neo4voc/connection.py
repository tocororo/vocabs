# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

""" Aplication Interface """

from neo4j import Driver, Result, Session, GraphDatabase, basic_auth

NEO4J_USERNAME = 'neo4j'
"""Username value for the Neo4j data base."""

NEO4J_PASSWORD = 'neo4j'
"""Password value for the Neo4j data base."""

NEO4J_DRIVER_HOST = 'localhost'
"""Driver value for the Neo4j data base."""

NEO4J_DRIVER_DB = 'neo4j'
"""Driver value for the Neo4j data base."""


class Connection(object):
    """
        Implements two design patterns, Facade and Singleton to create a unique instance and an interface between this module and Neo4j module.
        Class that gives a connection and the basic operations with Neo4j data base.

            load from current app config 3 values: \n
            `NEO4J_DRIVER_HOST` : IP direction or URL\n
            `NEO4J_USERNAME` : User name with privilages in Neo4j data base\n
            `NEO4J_PASSWORD` : Password to auth
    """
    # itself instance, following with Singleton desing pattern
    instance = None

    # driver of connection
    __driver: Driver = None
    __session: Session = None

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
            `NEO4J_DRIVER_HOST` : IP address or URL\n
            `NEO4J_USERNAME` : User name with privilages in Neo4j data base\n
            `NEO4J_PASSWORD` : Password to auth
        """

        if (not NEO4J_DRIVER_HOST or
                not NEO4J_USERNAME or
                not NEO4J_PASSWORD):
            raise Exception("missing arguments to set up a connection with Neo4j data base")

        uri = "bolt://" + NEO4J_DRIVER_HOST + ":7687"
        username = NEO4J_USERNAME
        password = NEO4J_PASSWORD
        self.__driver = GraphDatabase.driver(uri, auth=(username, password),
                                             encrypted=False)
        self.__driver.verify_connectivity()
        self.__session = self.__driver.session(database=NEO4J_DRIVER_DB)

    def close(self):
        """ Closes the connection with Neo4j data base """
        self.__driver.close()
        self.__session.close()

    def query(self, query: str):
        """ Executes a query and returns the result. """
        return self.__driver.execute_query(query)
        

    def create(self, query: str):
        """ Executes a `create` query and returns the result.
        This function also makes a commit into data base. """
        with self.__driver.session(database=NEO4J_DRIVER_DB) as session:
            transaction = session.begin_transaction()
            n = transaction.run(query).single().value()
            transaction.commit()
            return n

    def database_all_info(self):
        """ Returns the graph """

        records, summary, keys = self.__driver.execute_query(
            'MATCH(n) RETURN n;',
            database_=NEO4J_DRIVER_DB,
        )
        return records

    def delete_all_info(self):
        """ Returns the graph """

        records, summary, keys = self.__driver.execute_query(
            'MATCH (n) DETACH DELETE n',
            database_=NEO4J_DRIVER_DB,
        )
        return records