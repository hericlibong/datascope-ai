# Generated migration for adding THEME entity type

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('analysis', '0002_angle_datasetsuggestion_entity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='type',
            field=models.CharField(choices=[('PER', 'Person'), ('ORG', 'Organization'), ('LOC', 'Location'), ('THEME', 'Theme'), ('DATE', 'Date'), ('NUM', 'Number'), ('MISC', 'Misc')], max_length=6),
        ),
    ]
