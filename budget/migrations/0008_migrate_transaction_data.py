from django.db import migrations

def migrate_expense_data(apps, schema_editor):
    Receipt = apps.get_model('budget', 'Receipt')
    ExpenseData = apps.get_model('budget', 'ExpenseData')
    
    for expense in ExpenseData.objects.select_related('receipt').all():
        receipt = expense.receipt
        receipt.date = expense.date
        receipt.amount = expense.amount
        receipt.counterparty = expense.vendor
        receipt.category = expense.category
        receipt.description = expense.description
        receipt.modified_by_user = expense.modified_by_user
        receipt.save()

def migrate_income_data(apps, schema_editor):
    Receipt = apps.get_model('budget', 'Receipt')
    IncomeData = apps.get_model('budget', 'IncomeData')
    
    for income in IncomeData.objects.select_related('receipt').all():
        receipt = income.receipt
        receipt.date = income.date
        receipt.amount = income.amount
        receipt.counterparty = income.payer
        receipt.category = income.category
        receipt.description = income.description
        receipt.modified_by_user = income.modified_by_user
        receipt.save()

def reverse_migration(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('budget', '0007_add_transaction_fields_to_receipt'),
    ]
    
    operations = [
        migrations.RunPython(migrate_expense_data, reverse_migration),
        migrations.RunPython(migrate_income_data, reverse_migration),
    ]
