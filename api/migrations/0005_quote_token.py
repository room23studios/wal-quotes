# Generated by Django 2.0.3 on 2018-03-12 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20180312_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='token',
            field=models.TextField(blank=True, null=True, unique=True),
        ),
    ]
