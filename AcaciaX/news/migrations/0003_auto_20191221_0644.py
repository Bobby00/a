# Generated by Django 2.2 on 2019-12-21 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20191221_0554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='image',
            field=models.ImageField(default='none', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='newscategory',
            name='name',
            field=models.CharField(default='none', max_length=30, unique=True),
        ),
    ]