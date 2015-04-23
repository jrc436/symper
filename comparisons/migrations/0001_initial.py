# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'')),
                ('group', models.CharField(max_length=4, choices=[(b'p6m', b'p6m'), (b'p6', b'p6'), (b'p31m', b'p31m'), (b'p3m1', b'p3m1'), (b'p3', b'p3'), (b'p4g', b'p4g'), (b'p4m', b'p4m'), (b'p4', b'p4'), (b'cmm', b'cmm'), (b'pgg', b'pgg'), (b'pmg', b'pmg'), (b'pmm', b'pmm'), (b'cm', b'cm'), (b'pg', b'pg'), (b'pm', b'pm'), (b'p2', b'p2'), (b'p1', b'p1')])),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice1', models.ForeignKey(related_name='oneset', to='comparisons.Image')),
                ('choice2', models.ForeignKey(related_name='twoset', to='comparisons.Image')),
                ('test_image', models.ForeignKey(related_name='testset', to='comparisons.Image')),
            ],
        ),
    ]
