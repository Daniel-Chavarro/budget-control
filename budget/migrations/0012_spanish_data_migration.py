from django.db import migrations


def update_spanish_choices(apps, schema_editor):
    Receipt = apps.get_model('budget', 'Receipt')
    Category = apps.get_model('budget', 'Category')
    
    Receipt.objects.filter(status='pending_review').update(status='pendiente')
    Receipt.objects.filter(status='approved').update(status='aprobado')
    Receipt.objects.filter(status='rejected').update(status='rechazado')
    
    Receipt.objects.filter(receipt_type='income').update(receipt_type='ingreso')
    Receipt.objects.filter(receipt_type='expense').update(receipt_type='gasto')
    
    Category.objects.filter(category_type='income').update(category_type='ingreso')
    Category.objects.filter(category_type='expense').update(category_type='gasto')


def reverse_choices(apps, schema_editor):
    Receipt = apps.get_model('budget', 'Receipt')
    Category = apps.get_model('budget', 'Category')
    
    Receipt.objects.filter(status='pendiente').update(status='pending_review')
    Receipt.objects.filter(status='aprobado').update(status='approved')
    Receipt.objects.filter(status='rechazado').update(status='rejected')
    
    Receipt.objects.filter(receipt_type='ingreso').update(receipt_type='income')
    Receipt.objects.filter(receipt_type='gasto').update(receipt_type='expense')
    
    Category.objects.filter(category_type='ingreso').update(category_type='income')
    Category.objects.filter(category_type='gasto').update(category_type='expense')


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0011_receipt_receipts_status_bda324_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(update_spanish_choices, reverse_choices),
    ]
