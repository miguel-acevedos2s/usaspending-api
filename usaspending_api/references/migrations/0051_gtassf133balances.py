# Generated by Django 2.2.14 on 2020-12-04 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_delete_appropriationaccountbalancesquarterly'),
        ('references', '0050_auto_20201204_2000'),
    ]

    operations = [
        migrations.CreateModel(
            name='GTASSF133Balances',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiscal_year', models.IntegerField()),
                ('fiscal_period', models.IntegerField()),
                ('budget_authority_unobligated_balance_brought_forward_cpe', models.DecimalField(decimal_places=2, max_digits=23)),
                ('adjustments_to_unobligated_balance_brought_forward_cpe', models.DecimalField(decimal_places=2, max_digits=23)),
                ('obligations_incurred_total_cpe', models.DecimalField(decimal_places=2, max_digits=23)),
                ('budget_authority_appropriation_amount_cpe', models.DecimalField(decimal_places=2, max_digits=23)),
                ('borrowing_authority_amount', models.DecimalField(decimal_places=2, max_digits=23)),
                ('contract_authority_amount', models.DecimalField(decimal_places=2, max_digits=23)),
                ('spending_authority_from_offsetting_collections_amount', models.DecimalField(decimal_places=2, max_digits=23)),
                ('other_budgetary_resources_amount_cpe', models.DecimalField(decimal_places=2, max_digits=23)),
                ('obligations_incurred', models.DecimalField(decimal_places=2, max_digits=23)),
                ('deobligations_or_recoveries_or_refunds_from_prior_year_cpe', models.DecimalField(decimal_places=2, max_digits=23)),
                ('gross_outlay_amount_by_tas_cpe', models.DecimalField(decimal_places=2, max_digits=23)),
                ('unobligated_balance_cpe', models.DecimalField(decimal_places=2, max_digits=23)),
                ('total_budgetary_resources_cpe', models.DecimalField(decimal_places=2, max_digits=23)),
                ('disaster_emergency_fund_code', models.TextField(null=True)),
                ('tas_rendering_label', models.TextField(db_index=True, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('treasury_account_identifier', models.ForeignKey(db_column='treasury_account_identifier', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='gtas', to='accounts.TreasuryAppropriationAccount')),
            ],
            options={
                'db_table': 'gtas_sf133_balances',
                'managed': True,
                'unique_together': {('fiscal_year', 'fiscal_period', 'disaster_emergency_fund_code', 'tas_rendering_label')},
            },
        ),
    ]
