# Generated by Django 3.2.8 on 2021-10-14 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='is_availble',
            new_name='is_available',
        ),
    ]
