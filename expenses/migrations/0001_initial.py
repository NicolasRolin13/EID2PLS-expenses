# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6, editable=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('repayment', models.BooleanField(default=False, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtendedUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transfert',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('date', models.DateTimeField(auto_now=True)),
                ('child_of_bill', models.ForeignKey(to='expenses.Bill', related_name='transferts')),
                ('receiver', models.ForeignKey(to='expenses.ExtendedUser', related_name='receivers')),
                ('sender', models.ForeignKey(to='expenses.ExtendedUser', related_name='senders')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bill',
            name='category',
            field=models.ManyToManyField(to='expenses.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bill',
            name='creator',
            field=models.ForeignKey(to='expenses.ExtendedUser'),
            preserve_default=True,
        ),
    ]
