# Generated by Django 3.2.21 on 2024-01-28 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_codeduel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codeduel',
            name='opponent',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]
