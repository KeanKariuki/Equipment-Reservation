from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_resource_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='resources/%Y/%m/'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='image_url',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
