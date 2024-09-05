# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds more fun to the platform."""

# TODO: This is an example file. Remove it if your package does not use any
# extra configuration variables.

from iroko_graph.deployment import *


IROKO_GRAPH_DEFAULT_VALUE = 'foobar'
"""Default value for the application."""

IROKO_GRAPH_BASE_TEMPLATE = 'iroko_graph/base.html'
"""Default base template for the demo page."""

IROKO_GRAPH_SCHEMA_PROPERTIES = dict(
    records= dict(
        searcher= IrokoSearcher.metadata.scan, 
            # Is a function that return a iterable of record object, required
        identifiers= [],
            # is a str array or a fucntion with all identifiers of the node, required
        labels= 'Article',
            # is a `str` can be a word or if has more that ones must be with this structure `Label1:Label2:Label3 ...`
            # which recommended style are camel case, beginning with an upper-case character. Example  'VehicleOwner'
        relationships= dict(
            # specifies properties that means relationships with other nodes
            creator= dict(
                identifiers= [],
                    # can be a str array or a `function` that return a str array, required
                labels= 'Person:Profesor',
                    # is a `str` can be a word or if has more that ones must be with this structure `Label1:Label2:Label3 ...`
                    # which recommended style are camel case, beginning with an upper-case character. Example  'VehicleOwner'
                properties= dict(),
                    # can be a `dict` or a `function` that return a `dict`, not required,
                    # if the node is other schema only needs identifiers, labels and how relate with the record in this case
                relationData=dict(
                    labels= 'WRITEN_BY',
                        # can be a word which recommended style are upper-case character. Example  'LIVE_IN'
                    properties= dict(),
                        # is a `dict` with the relation data
                    direction= '->'
                )
            ),
            source= dict(
                identifier=dict(issn='123-124-124', ),
                labels= 'RevistaCientifica'

            )
        )
    )
)