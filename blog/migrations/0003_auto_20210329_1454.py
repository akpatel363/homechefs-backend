# Generated by Django 3.1.6 on 2021-03-29 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_recipe_stars'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='stars',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=2),
        ),
    ]