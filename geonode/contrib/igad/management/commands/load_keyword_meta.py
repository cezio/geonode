#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function


import os
import csv
from django.utils.translation import ugettext_lazy as _
from django.core.management.base import BaseCommand, CommandError
from geonode.contrib.igad.models import HierarchicalKeywordMeta
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
    Load keyword meta from csv.

    Structure should be hieriarchical:
    
    keyword, title, icon, description, url

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
            HierarchicalKeywordMeta.objects.all().delete()
        else:
            raise CommandError("No options selected")

    def set_keywords(self, data):
        """
        Creates keyword objects
        """
        for term in data:
            print('adding term meta', term) #['hkeywowrd'], term['title'])
            hk = term.pop('hkeyword')
            try:
                hkm = HierarchicalKeywordMeta.objects.get(hkeyword__name=hk)
            except HierarchicalKeywordMeta.DoesNotExist:
                hk = HierarchicalKeyword.objects.get(name=hk)
                hkm = HierarchicalKeywordMeta.objects.create(hkeyword=hk, title=term)

            hkm.update(**term)
            hkm.save()

    def parse_file(self, fname, **dialect):
        """
        Parses csv (comma, quote cells with comma), returns list of
        items:
        (term, parent term (or None if root), depth)

        """

        # triples of term, parent, indent
        out = []

        header = ('hkeyword', 'title', 'icon', 'description', 'url',)
        with open(fname, 'rt') as f:
            r = csv.reader(f, **dialect)
            for l in r:
                item = dict(zip(header, map(str.strip, l)))
                if not item['hkeyword'] or not item['title']:
                    continue
                out.append(item)

        return out
