# Views, urlpatterns vs  viewsets and routers
ViewSets and Routers are simple tools to speed up the implementation of your API if you're aiming for standard behaviour and standard URLs.

Using ViewSet you don't have to create separate views for getting a list of objects and detail of one object. ViewSet will handle for you in a consistent way both list and detail.

Using Router will connect your ViewSet into "standarized" (it's not standard in any global way, just some structure that was implemented by creators of Django REST framework) structure of URLs. That way you don't have to create your urlpatterns by hand and you're guaranteed that all of your URLs are consistent (at least on the layer that Router is responsible for).

It looks like not much, but when implementing some huge API where you will have many and many urlpatterns and views, using ViewSets and Routers will make big difference.

For better explanation: this is code using ViewSets and Routers:
```python
# views.py:

from snippets.models import Article
from rest_framework import viewsets
from yourapp.serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
# urls.py:

from django.urls import re_path as url, include
from yourapp import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
```
```python
And equivalent result using normal Views and no routers:

# views.py:

from snippets.models import Article
from snippets.serializers import ArticleSerializer
from rest_framework import generics


class ArticleList(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
urls.py

from django.urls import re_path as url, include
from yourapp import views

urlpatterns = [
    url(r'articles/^', views.ArticleList.as_view(), name="article-list"),
    url(r'articles/(?P<pk>[0-9]+)/^', views.ArticleDetail.as_view(), name="article-detail"),
]
```