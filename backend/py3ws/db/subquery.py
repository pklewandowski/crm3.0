from django.db import models


class SubQuerySum(models.Subquery):
    output_field = models.DecimalField()

    def __init__(self, name, *args, **kwargs):
        models.Subquery.__init__(self, *args, **kwargs)
        self.queryset = self.queryset.annotate(total=models.Sum(name)).values("total")
        self.queryset.query.set_group_by()  # values() adds a GROUP BY we don't want here
