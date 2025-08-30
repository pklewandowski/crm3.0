from . import HIERARCHY_TYPE_STATUS


def get_department(hierarchy):
    h = hierarchy
    while h.type != HIERARCHY_TYPE_STATUS['department']:
        h = h.parent
        if not h:
            return None
    return h


def get_departments(hierarchy_set, with_descendants=False):
    depts = {}
    for h in hierarchy_set:
        dept = get_department(h)
        if dept:
            depts[dept.pk] = dept
            if with_descendants:
                for dsc in dept.get_descendants():
                    depts[dsc.pk] = dsc
    return depts

def check_user_perms(user, status_hierarchies, raise_exception=False):
    if user.is_superuser:
        return True

    if not status_hierarchies:
        return True

    user_hierarchies = user.hierarchy.all()

    if not user_hierarchies:
        return False

    for hierarchy in status_hierarchies:
        if hierarchy in user_hierarchies:
            return True

    return False
