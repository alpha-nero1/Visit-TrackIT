# Generated by Django 3.2.4 on 2021-07-01 07:34

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0004_alter_domain_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='domain',
            unique_together={('name', 'user')},
        ),
    ]
