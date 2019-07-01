# Generated by Django 2.2.1 on 2019-05-15 12:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medrecord', '0002_auto_20190513_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='MKXfull',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('level', models.IntegerField()),
                ('code_full', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=512)),
                ('name_en', models.CharField(max_length=512)),
            ],
        ),
        migrations.AlterField(
            model_name='mrdiagnosis',
            name='mkx',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medrecord.MKXfull'),
        ),
        migrations.DeleteModel(
            name='MKX',
        ),
    ]
