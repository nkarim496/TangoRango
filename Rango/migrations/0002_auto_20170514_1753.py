# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-14 14:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rango', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.AddField(
            model_name='page',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]