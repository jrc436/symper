# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0004_auto_20150423_0545'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='elapsedTime',
            field=models.PositiveIntegerField(default=3),
        ),
        migrations.AlterField(
            model_name='result',
            name='correct',
            field=models.SmallIntegerField(default=0, choices=[(1, b'correct'), (0, b'timeout'), (2, b'incorrect')]),
        ),
    ]
