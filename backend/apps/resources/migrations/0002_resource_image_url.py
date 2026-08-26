from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='image_url',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
