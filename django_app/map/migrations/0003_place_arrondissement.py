from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0002_place_mainlevee'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='arrondissement',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
    ]
