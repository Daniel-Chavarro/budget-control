"""Delete Unit and UserUnit models."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0009_remove_old_tables'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserUnit',
        ),
        migrations.DeleteModel(
            name='Unit',
        ),
    ]
