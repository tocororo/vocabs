# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Manage fixtures for INSPIRE site."""

from __future__ import absolute_import, division, print_function

import click
from flask.cli import with_appcontext
from .neo4j import load_data


@click.group()
def fixtures():
    """Command related to migrating/init iroko data."""


@fixtures.command()
@with_appcontext
def initneo4jimportdata():
    """Init Neo4j import data."""
    load_data()








