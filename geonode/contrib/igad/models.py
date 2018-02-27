#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from django.db import models

from geonode.base.models import HierarchicalKeyword
# Create your models here.


class HierarchicalKeywordMeta(models.Model):
    hkeyword = models.ForeignKey(HierarchicalKeyword, related_name='meta')
    icon = models.CharField(max_length=128, null=False)
    title = models.CharField(max_length=128, null=True)
    description = models.TextField(null=True)
    url = models.URLField(null=True)

    @classmethod
    def get_keywords(cls):
        return HierarchicalKeyword.objects.filter(meta__isnull=False)


    def update(self, **attrs):
        for attr, val in attrs.items():
            setattr(self, attr, val)
