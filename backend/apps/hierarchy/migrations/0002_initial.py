# Generated by Django 5.0.7 on 2024-07-27 12:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0013_group_description'),
        ('hierarchy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='hierarchy',
            name='manager',
            field=models.ForeignKey(blank=True, db_column='id_manager', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manager', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hierarchy',
            name='parent',
            field=models.ForeignKey(blank=True, db_column='parent', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='hierarchy.hierarchy'),
        ),
        migrations.AddField(
            model_name='hierarchygroup',
            name='group',
            field=models.ForeignKey(db_column='id_group', on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
        ),
        migrations.AddField(
            model_name='hierarchygroup',
            name='hierarchy',
            field=models.ForeignKey(db_column='id_hierarchy', on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='hierarchy.hierarchy'),
        ),
        migrations.AddField(
            model_name='hierarchy',
            name='hierarchy_groups',
            field=models.ManyToManyField(through='hierarchy.HierarchyGroup', to='auth.group'),
        ),
        migrations.AddField(
            model_name='hierarchyposition',
            name='hierarchy',
            field=models.ForeignKey(db_column='id_hierarchy', on_delete=django.db.models.deletion.CASCADE, related_name='position_set', to='hierarchy.hierarchy'),
        ),
    ]
