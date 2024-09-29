from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.user.models import User


class Project(models.Model):
    manager = models.ForeignKey(User, db_column='id_manager', related_name='project_manager', on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_('project.name'), max_length=300)
    description = models.TextField(verbose_name=_('project.description'), null=True, blank=True)
    code = models.CharField(verbose_name=_('project.code'), max_length=20)
    start_date = models.DateField(verbose_name=_('project.start_date'))
    uat_date = models.DateField(verbose_name=_('project.uat_date'), null=True, blank=True)
    end_date = models.DateField(verbose_name=_('project.end_date'), null=True, blank=True)
    total_hours = models.IntegerField(verbose_name=_('project.total_hours'))

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'project'


class ProjectModule(models.Model):
    manager = models.ForeignKey(User, db_column='id_manager', related_name='module_manager', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, db_column='id_project', related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_('project.module.name'), max_length=300)
    description = models.TextField(verbose_name=_('project.description'), null=True, blank=True)
    code = models.CharField(verbose_name=_('project.module.code'), max_length=20)
    start_date = models.DateField(verbose_name=_('project.module.start_date'), null=True, blank=True)
    uat_date = models.DateField(verbose_name=_('project.module.uat_date'), null=True, blank=True)
    end_date = models.DateField(verbose_name=_('project.module.end_date'), null=True, blank=True)
    status = models.CharField(verbose_name=_('project.module.status'), max_length=10)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'project_module'


class ProjectTask(models.Model):
    module = models.ForeignKey(ProjectModule, db_column='id_module', related_name='tasks', on_delete=models.CASCADE)
    developer = models.ForeignKey(User, db_column='id_developer', related_name='task_developers', on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_('project.tesk.name'), max_length=300)
    description = models.TextField(verbose_name=_('project.task.description'), null=True, blank=True)
    start_date = models.DateTimeField(verbose_name=_('project.task.start_date'), null=True, blank=True)
    end_date = models.DateTimeField(verbose_name=_('project.task.end_date'), null=True, blank=True)
    total_minutes = models.IntegerField()
    status = models.CharField(verbose_name=_('project.task.status'), max_length=10)
    priority = models.CharField(verbose_name=_('project.task.priority'), max_length=20)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'project_task'


class ProjectTaskTime(models.Model):
    task = models.ForeignKey(ProjectTask, db_column='id_task', related_name='task_times', on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_('project.module.name'), max_length=300, null=True, blank=True)
    description = models.TextField(verbose_name=_('project.description'), null=True, blank=True)
    uid = models.CharField(verbose_name=_('project.task.time.uid'), max_length=100)
    start = models.DateTimeField(verbose_name=_('project.task.time.start'))
    end = models.DateTimeField(verbose_name=_('project.task.time.end'), null=True)

    class Meta:
        db_table = 'project_task_time'
