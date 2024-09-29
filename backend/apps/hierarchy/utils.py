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
