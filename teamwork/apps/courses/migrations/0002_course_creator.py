# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 23:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='creator',
            field=models.CharField(default='No admin lol', max_length=255),
        ),
    ]