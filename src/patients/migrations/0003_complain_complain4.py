# Generated by Django 2.1.3 on 2018-12-13 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_auto_20181211_2214'),
    ]

    operations = [
        migrations.AddField(
            model_name='complain',
            name='complain4',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
