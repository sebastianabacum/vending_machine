# Generated by Django 4.2.2 on 2023-08-07 10:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vending", "0004_buyer"),
    ]

    operations = [
        migrations.AddField(
            model_name="buyer",
            name="email",
            field=models.EmailField(default="abacum@abacum.io", max_length=254),
        ),
    ]