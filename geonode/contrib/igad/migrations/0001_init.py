# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_auto_20171114_0341'),
    ]

    operations = [
        migrations.CreateModel(
            name='HierarchicalKeywordMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('icon', models.CharField(max_length=128)),
                ('title', models.CharField(max_length=128, null=True)),
                ('description', models.TextField(null=True)),
                ('url', models.URLField(null=True)),
                ('hkeyword', models.ForeignKey(related_name='meta', to='base.HierarchicalKeyword')),
            ],
        ),
    ]
