# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from jsonschema.validators import validate
from iroko_graph.query import CreateNode, CreateRelationship

class Facade:

    __schema: dict


    def __init__(self, **kwargs):
        """

        """
        if 'schema' in kwargs: self.__schema = kwargs['schema']
        self.__schema = dict(
        {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "id": "https://localhost:5000/schemas/source.json",
            "type": "object",
            "definitions": {

            },
            "properties": {
                "uuid": { "type": "string" },
                "name": { "type": "string" },
                "source_type": { "type": "string" },
                "source_status": { "type": "string" },
                "terms": {
                    "type": "array",
                    "items": {
                        "$ref": "https://localhost:5000/schemas/term_sources.json",
                        "properties": {
                            "data": { "type": "string" }
                        }
                    }
                },
                "versions": {
                    "type": "array",
                    "items": {
                        "$ref": "https://localhost:5000/schemas/source_version.json",
                        "publish_date": "date"
                    }
                },
                "creator": {
                    "type": "object",
                    "properties": {
                        "$ref": "https://localhost:5000/schemas/person.json",
                        "rol": "string",
                        "other": "date"
                    }
                },
                "data": { "type": "string" }
            },
            "required": ["uuid", "name"]
        })
        {
            "uuid": "bla",
            "name": "bla",
            "source_type": "bla",
            "source_status": "bla",
            "terms": [
                {
                    "$ref": "https://sceiba.cu/skos/term/cuco",
                    "fecha": "20/2/12"
                },
                {
                    "$ref": "https://sceiba.cu/skos/term/paco",
                    "fecha": "20/2/12"
                }
            ]
        }
        self.relationship = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "id": "https://localhost:5000/schemas/source_version.json",
            "type": "object",
            "properties":{
                "source": {
                    "$ref": "https://....source",
                    "properties": {
                        "ids":''
                    }
                },
                "version": {
                    "$ref": "https://....version",
                    "properties": { " los identifiers del otro nodo "}
                },
                "data": {
                    "type": "object",
                    "properties":{ ... }
                }
            }
        }
        self.mapping = {
            "first_node": {
                "uuid": "weirhui234hn3iu4h5n",
                "pidstore": "24234345fdetber",
                "record_id": "123abc",
                # "otros": "pueden ser todos los identifiers de un nodo lo que hay q especificarlo en el schema"
            },
            "second_node": {
                "pidstore": "etrytuyu9b5rv46fv65f",
                "publisher_id": "autor id"
            },
            "data": {
                "written": "2020",
                "":''
                # "otras propiedades de la relacion": "con sus datos"
            }
        }

    @property
    def schema(self):
        """ Gets the JSON schema. """
        return self.__schema

    @schema.setter
    def schema(self, schema: dict= dict()):
        """ Changes the JSON schema. """
        self.__schema = schema


    def validate(self, dictionary: dict):
        """ Validates if a new `dict` is valid with a schema """
        try:
            validate(dictionary, self.__schema)
        except Exception as e:
            return str(e)


    def create_node(self, dictionary: dict, label: str, identifiers: dict=None):
        """
            Creates a node in Neo4j data base. \n
            :Arguments:
                element_type: can be `NODE_TYPE` or `RELATIONSHIP_TYPE`\n
                identifiers: is a `dict` but if it is `None`, then the algorithm search in field `required` in the schema
        """
        valid = self.validate(dictionary)
        if valid is not None: raise Exception(valid)

        identify = dict()
        if identifiers is not None:
            identify = identifiers
        else:
            if 'required' not in self.__schema:
                raise Exception("Keyword 'required' must be in schema")

            for k in self.__schema['required']:
                identify[k] = dictionary[k]

        node = CreateNode()
        node.build(
            identifier= identify,
            properties= dictionary,
            labels= label)
        node.execute()

    def create_relationiship(self, source_node: dict, target_node: dict, properties: dict):
        pass


