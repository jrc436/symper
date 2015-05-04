# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PUser',
            fields=[
                ('turk_id', models.PositiveIntegerField(serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaskSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tasks', models.ManyToManyField(to='comparisons.Task')),
            ],
        ),
        migrations.AddField(
            model_name='puser',
            name='taskset',
            field=models.ForeignKey(to='comparisons.TaskSet'),
        ),
    ]
