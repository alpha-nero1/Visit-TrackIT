# Generated by Django 3.2.4 on 2021-07-01 02:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Visits',
            new_name='Visit',
        ),
    ]