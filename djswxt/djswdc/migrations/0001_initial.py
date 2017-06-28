# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-11 08:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djswdc.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='dc_data',
            fields=[
                ('num', models.IntegerField(primary_key=True, serialize=False)),
                ('uid', models.CharField(max_length=30, unique=True)),
                ('breakfast_book', djswdc.models.ListTextField(default=[])),
                ('lunch_book', djswdc.models.ListTextField(default=[])),
                ('dinner_book', djswdc.models.ListTextField(default=[])),
                ('breakfast_eat', djswdc.models.ListTextField(default=[])),
                ('lunch_eat', djswdc.models.ListTextField(default=[])),
                ('dinner_eat', djswdc.models.ListTextField(default=[])),
                ('other_eat', djswdc.models.ListTextField(default=[])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
