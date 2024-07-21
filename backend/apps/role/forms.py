from .models import Role
from py3ws.forms import p3form


class RoleForm(p3form.ModelForm):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'parent']
