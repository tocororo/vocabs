# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Iroko-Graph is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Fixtures extension."""

from __future__ import absolute_import, division, print_function

from .cli import fixtures


class IrokoGraphFixtures(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.cli.add_command(fixtures)
        app.extensions['iroko-graph-fixtures'] = self
