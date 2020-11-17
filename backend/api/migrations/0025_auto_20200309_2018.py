# Generated by Django 3.0.3 on 2020-03-10 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_auto_20200306_0050'),
    ]

    operations = [
        migrations.AddField(
            model_name='salessubmission',
            name='submission_sequence',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='salessubmission',
            unique_together={('submission_date', 'submission_sequence', 'organization')},
        ),
        migrations.RemoveField(
            model_name='salessubmission',
            name='name',
        ),
    ]