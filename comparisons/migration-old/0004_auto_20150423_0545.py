# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0003_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='puser',
            name='dead',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='result',
            name='correct',
            field=models.BooleanField(default=False),
        ),
    ]
