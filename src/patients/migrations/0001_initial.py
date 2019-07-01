# Generated by Django 2.1.3 on 2018-11-28 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mis', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('index', models.CharField(max_length=5, null=True)),
                ('district', models.CharField(max_length=64, null=True)),
                ('city', models.CharField(max_length=255, null=True)),
                ('street', models.CharField(max_length=255, null=True)),
                ('building', models.CharField(blank=True, max_length=255, null=True)),
                ('apartment', models.CharField(max_length=16, null=True)),
                ('address_comment', models.CharField(max_length=255, null=True)),
                ('longitude', models.CharField(max_length=64, null=True)),
                ('latitude', models.CharField(max_length=64, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('address_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis.AddressType')),
                ('location_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis.LocationType')),
            ],
        ),
        migrations.CreateModel(
            name='Complain',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('complain1', models.CharField(blank=True, max_length=255, null=True)),
                ('complain2', models.CharField(blank=True, max_length=255, null=True)),
                ('complain3', models.CharField(blank=True, max_length=255, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, default='НЕВІДОМИЙ', max_length=64)),
                ('first_name', models.CharField(blank=True, max_length=64, null=True)),
                ('family_name', models.CharField(blank=True, max_length=64, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=64, null=True)),
                ('age', models.CharField(blank=True, max_length=64, null=True)),
                ('sex', models.CharField(max_length=16, null=True)),
                ('phone', models.CharField(blank=True, max_length=32, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]