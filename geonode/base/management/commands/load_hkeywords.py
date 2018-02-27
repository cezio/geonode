#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

#########################################################################
#
# Copyright (C) 2018 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os
import csv
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from geonode.base.models import HierarchicalKeyword


def isfile(path):
    """
        path validator
    """
    if os.path.exists(path) and os.path.isfile(path):
        return path
    raise CommandError("Invalid path: {}".format(path))


class Command(BaseCommand):
    """
    Load keywords from csv.

    Structure should be hieriarchical:

    keyword1,
    ,subkeyword1
    ,subkeyword2
    ,,subsubkeyword3

    Default csv params:
        * comma separated
        * cells quoted
    """

    help = "Load keywords from csv"

    def add_arguments(self, parser):
        parser.add_argument('path',
                            type=isfile,
                            nargs='?',
                            default=None,
                            help=_("Parse this file")
                           )
        parser.add_argument('-c', '--clear',
                                  action='store_true',
                                  dest='clear',
                                  default=False,
                                  help=_("Clear hierarchical keywords"))
        return parser

    def handle(self, **options):
        path = options['path']
        if path:
            print('parsing', path)
            parsed = self.parse_file(path)
            self.set_keywords(parsed)
        elif options['clear']:
            print('clearing hkeywords')
            HierarchicalKeyword.objects.all().delete()
        else:
            raise CommandError("No options selected")

    def set_keywords(self, data):
        """
        Creates keyword objects
        """
        for term, parent, lvl in data:
            if parent:

                print('adding child', parent, '->', term)
                t = HierarchicalKeyword.objects.get(name=parent)
                try:
                    HierarchicalKeyword.objects.get(name=term)
                except HierarchicalKeyword.DoesNotExist:
                    t.add_child(name=term)
            else:
                print('adding root', term)
                try:
                    HierarchicalKeyword.objects.get(name=term)
                except HierarchicalKeyword.DoesNotExist:
                    HierarchicalKeyword.add_root(name=term)

    def parse_file(self, fname, **dialect):
        """
        Parses csv (comma, quote cells with comma), returns list of
        items:
        (term, parent term (or None if root), depth)

        """

        # triples of term, parent, indent
        out = []

        def get_previous(at_level):
            if out:
                for o in out[::-1]:
                    if o[-1] == at_level:
                        return o

            return (None, None, 0)

        def get_current(row):
            for ridx, item in enumerate(row):
                if item:
                    return (item.strip().decode('utf-8'), ridx,)

        with open(fname, 'rt') as f:
            r = csv.reader(f, **dialect)
            for l in r:
                this = get_current(l)
                # skip empty lines
                if not this:
                    continue
                this_term, this_level = this
                prev = get_previous(this_level-1)
                prev_item, prev_parent, prev_level = prev
                this_parent = prev_item
                out.append((this_term, this_parent, this_level))

        return out
