# Generated by Django 3.1.1 on 2020-09-16 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_inviterelation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verifycode',
            name='user',
        ),
        migrations.AddField(
            model_name='verifycode',
            name='mobile',
            field=models.CharField(default='', max_length=14, verbose_name='Mobile'),
        ),
    ]
