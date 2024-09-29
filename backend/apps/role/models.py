from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.

class Role(MPTTModel):
    name = models.CharField(max_length=200)
    parent = TreeForeignKey('self', blank=True, null=True, db_column="parent", related_name='children', on_delete=models.CASCADE)
    description = models.TextField()
    is_client_role = models.BooleanField(default=False)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        db_table = "role"

    def publish(self):
        self.save()

    def __str__(self):
        return self.name


class Privilege(models.Model):
    name = models.CharField(max_length=200)
    controller = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        db_table = "privilege"

    def publish(self):
        self.save()

    def __str__(self):
        return self.name


class RolePrivilege(models.Model):
    role = models.ForeignKey(Role, db_column="id_role", on_delete=models.CASCADE)
    privilege = models.ForeignKey(Privilege, db_column="id_privilege", on_delete=models.CASCADE)

    class Meta:
        db_table = "role_privilege"
