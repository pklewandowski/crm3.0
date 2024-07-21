from django.db import models


# Create your models here.
class TagCatergory(models.Model):
    name = models.CharField(max_length=300, verbose_name='tag.category.name')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tag_category'


class Tag(models.Model):
    category = models.ForeignKey(TagCatergory, db_column='id_category', on_delete=models.CASCADE)
    name = models.CharField(max_length=300, verbose_name='tag.name')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tag'
