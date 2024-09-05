# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


from flask import current_app
from iroko_graph.query import CreateNode, CreateRelationship, DIRECTED

def load_data():
    """
        load data
    """
    print('import data START!!!')

    if not current_app.config['IROKO_GRAPH_SCHEMA_PROPERTIES']:
        raise Exception("Missing arguments `IROKO_GRAPH_SCHEMA_PROPERTIES` to import data")

    if type(current_app.config['IROKO_GRAPH_SCHEMA_PROPERTIES']) is not dict:
        raise Exception("Arguments `IROKO_GRAPH_SCHEMA_PROPERTIES` must be a `dict`")

    # recorrer todos los esquemas de la configuracion para importar sus datos
    schemas = current_app.config['IROKO_GRAPH_SCHEMA_PROPERTIES']
    for key in schemas:

        # validar que cada esquema sea un diccionario
        if type(schemas[key]) is not dict:
            raise Exception("The schema {0} don't have a valid format".format(key))

        # validar que cada esquema tenga la propiedad `searcher` y sea un iterable
        if 'searcher'not in schemas[key]:
            raise Exception("The schema '{0}' don't have a searcher property".format(key))

        # validar que el `searcher` de cada esquema sea un iterable
        # if type(schemas[key]['searcher']) is It

        # para cada elemento crear el `Nodo` y las relaciones
        for node in schemas[key]['searcher']:

            # validar que existen los identificadores del nodo
            if 'identifiers' not in schemas[key]:
                raise Exception("The schema '{0}' don't have identifiers property".format(key))
            if type(schemas[key]['identifiers']) is not list:
                raise Exception("Identifiers on schema '{0}' don't have a valid format".format(key))

            # crear `dict` de identificadores del nodo
            identifiers = dict()
            for item in schemas[key]['identifiers']:
                identifiers[item]= node.metadata[item]

            # validar que existen los labels del nodo
            labels = ''
            if 'labels' not in schemas[key]:
                raise Exception("The schema '{0}' don't have lables property".format(key))
            labels = schemas[key]['labels']

            ### build a Neo4j node ###
            new_node = CreateNode()
            new_node.build(identifier= identifiers, properties= node.metadata, labels= labels)
            new_node.execute()
            print("Created NODE: {0}".format(identifiers))

            ### create relationships ###

            # validar que cada esquema tenga la propiedad `relationships` y sea un `dict`
            if 'relationships'not in schemas[key]:
                raise Exception("The schema '{0}' don't have a relationships property".format(key))
            if type(schemas[key]['relationships']) is not dict:
                raise Exception("Relationships on schema '{0}' don't have a valid format".format(key))

            # para cada `Nodo` crear sus relaciones
            relationships = schemas[key]['relationships']
            for relation_key in relationships:
                # -----------------------
                if 'identifiers' not in relationships[relation_key]:
                    raise Exception("Relationship '{0}' don't have a identifiers property".format(relation_key))

                relation_node_identifiers = dict()
                for item in relationships[relation_key]['identifiers']:
                    # `nodo` es cada elemento del `searcher`, en `metadata` estan las propiedades
                    # `relation_key` representa la propiedad que es una relación
                    # `item` es el propiedad de ese nodo que en el config se dijo es un identificador
                    relation_node_identifiers[item]= node.metadata[relation_key][item]

                # -----------------------
                if 'labels' not in relationships[relation_key]:
                    raise Exception("Relationship '{0}' don't have a labels property".format(relation_key))

                relation_node_labels = relationships[relation_key]['labels']

                ### ---- TODO: cambiar en el futuro 'properties' no son necesarias por ahora por tanto no se implementa,
                ### ---- solo nos quedamos con lo minimo necesario

                ### build a Neo4j node related ###
                new_node = CreateNode()
                new_node.build(identifier= relation_node_identifiers, properties= dict(), labels= relation_node_labels)
                new_node.execute()
                print("Created related NODE: {0}".format(relation_node_identifiers))

                # -----------------------
                # crear las relaciones
                if 'relationData' not in relationships[relation_key]:
                    raise Exception("Relationship '{0}' don't have a relationData property".format(relation_key))

                relation_data = relationships[relation_key]['relationData']

                if 'labels' not in relation_data:
                    raise Exception("RelationData in Relationship '{0}' don't have a labels property".format(relation_key))

                relation_data_label = relation_data['labels']

                relation_data_properties = dict()
                if 'properties' in relation_data:
                    relation_data_properties = relation_data['properties']

                ### build a Neo4j relationship ###
                new_relationship = CreateRelationship()
                new_relationship.build(nodes=[{'identifier': identifiers}, {'identifier': relation_node_identifiers}], label= relation_data_label, direction=DIRECTED)
                new_relationship.execute()
                print("Created RELATIONSHIP between: {0} and {1}".format(identifiers, relation_node_identifiers))

    print("import data END!!!")

