from django.shortcuts import render, redirect

from django.views import View
from django.views.generic import ListView

from apps.tag.forms import TagForm
from apps.tag.models import Tag


class TagListView(ListView):
    model = Tag
    paginate_by = 3
    ordering = 'name'


    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context


class TagView(View):
    def get(self, request, id=None):
        tag = Tag.objects.get(pk=id) if id else None
        form = TagForm(initial=tag)

        context = {"form": form}

        return render(request, 'tag/add.html', context)

    def post(self, request):
        form = TagForm(request.POST, instance=Tag.objects.get(pk=Tag.objects.get(pk=request.POST.get('id'))))
        if form.has_changed() and form.is_valid():
            form.save()
        return redirect('tag.edit', id=form.instance.pk)
