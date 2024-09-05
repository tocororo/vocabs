# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds more fun to the platform."""

# TODO: This is an example file. Remove it if you do not need it, including
# the templates and static folders as well as the test case.

from flask import Blueprint, render_template
from flask_babelex import gettext as _
from iroko_graph.query import CreateNode, CreateRelationship, UNDIRECTED

blueprint = Blueprint(
    'iroko_graph',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route("/")
def index():
    """Render a basic view."""
    return render_template(
        "iroko_graph/index.html",
        module_name=_('Iroko-Graph'))

@blueprint.route("/create")
def create():
    """Creates a graph in Neo4j data base"""

    node = CreateNode()
    node.build(identifier={ 'name': 'Edel' }, properties={ 'name': 'Edel', 'lastName': 'Abreu', 'age': 27 },labels="Person:Profesor:Informatics")
    node.execute()

    node.build(identifier={ 'name': 'Rafael' }, properties={ 'name': 'Rafael', 'lastName': 'Martinez Estevez', 'age': 36 },labels="Person:Profesor:ComputerScience")
    node.execute()

    node.build(identifier={ 'name': 'Eduardo' }, properties={ 'name': 'Eduardo', 'lastName': 'Cabeza', 'age': 36 },labels="Person:Profesor:Informatics:Master")
    node.execute()

    node.build(identifier={ 'name': 'Reinier' }, properties={ 'name': 'Reinier', 'lastName': 'Lorenzo Cabezas', 'age': 28 },labels="Person:Specialist:Informatics")
    node.execute()

    node.build(identifier={ 'name': 'Erdin' }, properties={ 'name': 'Erdin', 'lastName': 'Espinosa', 'age': 29 },labels="Person:Profesor:InformaticsScience:Master")
    node.execute()

    node.build(identifier={ 'name': 'Diego' }, properties={ 'name': 'Diego', 'lastName': 'Ferreiro', 'age': 29 },labels="Person:Profesor:InformaticsScience")
    node.execute()

    node.build(identifier={ 'name': 'Luis Enrique' }, properties={ 'name': 'Luis Enrique', 'lastName': 'Cabezas', 'age': 34 },labels="Person:Profesor:ComputerScience")
    node.execute()

    node.build(identifier={ 'name': 'Mabel' }, properties={ 'name': 'Mabel', 'lastName': 'Rodriguez', 'age': 50 },labels="Person:Profesor:Master")
    node.execute()


    node.build(identifier={ 'name': 'CRAI' }, properties={ 'name': 'CRAI', 'fullName': 'Centro de Recursos para el Aprendizaje y la Investigación' },labels="Center")
    node.execute()
    node.build(identifier={ 'name': 'UPR' }, properties={ 'name': 'UPR', 'fullName': 'Universidad de Pinar del Rio' },labels="Institution")
    node.execute()


    relationship = CreateRelationship()
    relationship.build(nodes=[{'identifier':{'name': 'Edel'}}, { 'labels': 'Person', 'identifier': {'name':'Rafael'}}], label="FRIEND", properties={'since': 2017}, direction=UNDIRECTED)
    relationship.execute()

    relationship.build(nodes=[{'identifier':{'name': 'Edel'}}, { 'labels': 'Person', 'identifier': {'name':'Reinier'}}], label="FRIEND", properties={'since': 2012}, direction=UNDIRECTED)
    relationship.execute()
    relationship.build(nodes=[{'identifier':{'name': 'Edel'}}, { 'labels': 'Person', 'identifier': {'name':'Diego'}}], label="FRIEND", properties={'since': 2016}, direction=UNDIRECTED)
    relationship.execute()

    relationship.build(nodes=[{'identifier':{'name': 'Edel'}}, { 'identifier': {'name':'CRAI'}}], label="WORK_IN", properties={'since': 2017})
    relationship.execute()
    relationship.build(nodes=[{'identifier':{'name': 'Rafael'}}, { 'identifier': {'name':'CRAI'}}], label="WORK_IN")
    relationship.execute()
    relationship.build(nodes=[{'identifier':{'name': 'Eduardo'}}, { 'identifier': {'name':'CRAI'}}], label="WORK_IN")
    relationship.execute()
    relationship.build(nodes=[{'identifier':{'name': 'Mabel'}}, { 'identifier': {'name':'CRAI'}}], label="WORK_IN")
    relationship.execute()
    relationship.build(nodes=[{'identifier':{'name': 'Erdin'}}, { 'identifier': {'name':'CRAI'}}], label="WORK_IN")
    relationship.execute()
    relationship.build(nodes=[{'identifier':{'name': 'Diego'}}, { 'identifier': {'name':'CRAI'}}], label="WORK_IN")
    relationship.execute()
    relationship.build(nodes=[{'identifier':{'name': 'Luis Enrique'}}, { 'identifier': {'name':'CRAI'}}], label="WORK_IN")
    relationship.execute()
    relationship.build(nodes=[{'identifier':{'name': 'Reinier'}}, { 'identifier': {'name':'CRAI'}}], label="WORK_IN")
    relationship.execute()

    relationship.build(nodes=[{'identifier':{'name': 'CRAI'}}, { 'identifier': {'name':'UPR'}}], label="BELONG")
    relationship.execute()

    return 'OK'
