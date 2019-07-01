# Generated by Django 2.2.2 on 2019-06-29 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0010_auto_20190109_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('level1', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=32)),
                ('capital', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('level1', models.CharField(max_length=10)),
                ('level2', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=32)),
                ('capital', models.CharField(max_length=32)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.State')),
            ],
        ),
        migrations.AddField(
            model_name='address',
            name='distr',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='patients.District'),
        ),
    ]
