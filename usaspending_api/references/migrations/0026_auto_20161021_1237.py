# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-21 16:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0025_auto_20161021_0948'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RefCFDAProgramInfo',
            new_name='CFDAProgram',
        ),
        migrations.AlterModelTable(
            name='cfdaprogram',
            table='cfda_program',
        ),
    ]
