# Generated by Django 3.1.1 on 2020-09-16 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20200915_0533'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='invite',
            field=models.CharField(max_length=11, null=True, verbose_name='Invitation Code'),
        ),
        migrations.AddField(
            model_name='verifycode',
            name='created',
            field=models.DateTimeField(auto_now=True, verbose_name='Created'),
        ),
    ]
