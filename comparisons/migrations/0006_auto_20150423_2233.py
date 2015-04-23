# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0005_auto_20150423_0634'),
    ]

    operations = [
        migrations.AddField(
            model_name='puser',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 23, 22, 33, 29, 60180, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='puser',
            name='git_revision',
            field=models.CharField(default=1, max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='puser',
            name='hit_id',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='puser',
            name='provisional',
            field=models.BooleanField(default=True),
        ),
    ]
