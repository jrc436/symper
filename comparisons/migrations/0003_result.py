# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0002_auto_20150420_0320'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=3, choices=[(b'TOP', b'choice1'), (b'BOT', b'choice2')])),
                ('selector', models.ForeignKey(to='comparisons.PUser')),
                ('task', models.ForeignKey(to='comparisons.Task')),
            ],
        ),
    ]
