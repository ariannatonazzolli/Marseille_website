from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='mainlevee',
            field=models.BooleanField(default=False),
        ),
    ]
