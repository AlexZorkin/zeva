# Generated by Django 3.0.14 on 2021-05-31 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0105_auto_20210526_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelyearreport',
            name='supplier_class',
            field=models.CharField(max_length=1, null=True),
        ),
    ]