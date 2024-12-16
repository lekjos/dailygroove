# Generated by Django 3.2.25 on 2024-12-16 18:44

from django.db import migrations


def add_initial_sites(apps, schema_editor):
    Site = apps.get_model("sites", "Site")

    sites = [
        {"id": 1, "domain": "dailygroove.us", "name": "Daily Groove"},
    ]

    # Create or update the sites
    for site_data in sites:
        Site.objects.update_or_create(id=site_data["id"], defaults=site_data)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_auto_20240307_0139"),
        ("sites", "__latest__"),
    ]

    operations = [
        migrations.RunPython(add_initial_sites),
    ]
