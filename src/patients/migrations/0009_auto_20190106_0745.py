# Generated by Django 2.1.3 on 2019-01-06 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0008_auto_20190106_0743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='situation',
            name='code_dsns',
            field=models.IntegerField(),
        ),
    ]
