from django.contrib.auth.models import Group
from django.db.models import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel

from application.models import CompanyDataMixin
from apps.address.models import Address
from apps.hierarchy import HIERARCHY_TYPE_STATUS


class Hierarchy(models.Model, CompanyDataMixin):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, db_column="parent", related_name='children', on_delete=models.CASCADE)
    description = models.TextField()
    address = models.ForeignKey(Address, db_column='id_address', related_name='address', null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    footer_disclaimer = models.TextField(null=True, blank=True)
    # type field accept values CMP - company | HDQ - headquarter | DEP - department | POS - position in department
    type = models.CharField(max_length=10, default=HIERARCHY_TYPE_STATUS['department'])
    manager = models.ForeignKey('user.User', db_column='id_manager', null=True, blank=True, related_name='manager', on_delete=models.SET_NULL)
    representative = JSONField(default=dict)
    is_client_role = models.BooleanField(default=False)
    hierarchy_groups = models.ManyToManyField(Group, through="HierarchyGroup")
    level = models.IntegerField()
    bank_transaction_files_directory = models.CharField(max_length=50, default='')
    bank_account = models.CharField(max_length=34, default='')
    sq = models.IntegerField(default=0)

    class Meta:
        db_table = "hierarchy"
        default_permissions = ('add', 'change', 'delete')
        permissions = (
            ('list_user', _('permissions.app.user.list_user')),
        )

    def get_children(self):
        return Hierarchy.objects.filter(parent=self)

    def is_root_node(self):
        return self.parent is None

    def move_to(self, hierarchy):
        self.parent = hierarchy
        self.level = hierarchy.level + 1
        self.save()

    def __str__(self):
        return self.name

    def is_headquarter(self):
        return True if self.objects.filter(type=HIERARCHY_TYPE_STATUS['headquarter']).count() else False


class HierarchyGroup(models.Model):
    hierarchy = models.ForeignKey(Hierarchy, db_column='id_hierarchy', related_name='groups', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, db_column='id_group', on_delete=models.CASCADE)

    class Meta:
        db_table = 'hierarchy_group'


class HierarchyPosition(models.Model):
    hierarchy = models.ForeignKey(Hierarchy, db_column='id_hierarchy', related_name='position_set', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, null=True, blank=True)
    sq = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'hierarchy_position'
