# Generated by Django 3.0.7 on 2021-07-22 15:00

import db_comments.model_mixins
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0113_auto_20210721_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditAgreementCreditTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('create_user', models.CharField(default='SYSTEM', max_length=130)),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('update_user', models.CharField(max_length=130, null=True)),
                ('credit_agreement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credit_agreement_credit_transaction', to='api.CreditAgreement')),
                ('credit_transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credit_agreement_credit_transaction', to='api.CreditTransaction')),
            ],
            options={
                'db_table': 'credit_agreement_credit_transaction',
            },
            bases=(models.Model, db_comments.model_mixins.DBComments),
        ),
    ]
