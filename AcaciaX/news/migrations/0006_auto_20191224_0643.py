# Generated by Django 2.2 on 2019-12-24 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_auto_20191224_0632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='image',
            field=models.ImageField(blank=True, upload_to='news'),
        ),
    ]
