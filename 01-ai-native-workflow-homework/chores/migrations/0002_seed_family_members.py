from django.db import migrations


def seed_family_members(apps, schema_editor):
    FamilyMember = apps.get_model('chores', 'FamilyMember')
    members = [
        {'name': 'Alice', 'role': 'parent'},
        {'name': 'Bob', 'role': 'parent'},
        {'name': 'Charlie', 'role': 'child'},
        {'name': 'Emma', 'role': 'child'},
    ]
    for m in members:
        FamilyMember.objects.get_or_create(name=m['name'], defaults={'role': m['role']})


def unseed_family_members(apps, schema_editor):
    FamilyMember = apps.get_model('chores', 'FamilyMember')
    FamilyMember.objects.filter(name__in=['Alice', 'Bob', 'Charlie', 'Emma']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('chores', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_family_members, reverse_code=unseed_family_members),
    ]
