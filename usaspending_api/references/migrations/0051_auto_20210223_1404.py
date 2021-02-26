# Generated by Django 2.2.18 on 2021-02-23 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0050_auto_20201208_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='gtassf133balances',
            name='anticipated_prior_year_obligation_recoveries',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=23),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gtassf133balances',
            name='prior_year_paid_obligation_recoveries',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=23),
            preserve_default=False,
        ),
    ]
