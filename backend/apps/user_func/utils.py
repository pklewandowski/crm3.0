from django.shortcuts import render, redirect
from py3ws.utils import utils
from apps.document.models import DocumentType
from apps.user.models import User
from django.utils import html


def list(request, code, page, search, filter_form=None):
    if code:
        document_type = DocumentType.objects.get(code=code)
    else:
        document_type = None
    document_types = DocumentType.objects.filter(is_product=True, is_active=True).order_by('name')

    sort_field = ''
    sort_dir = ''

    if filter_form:
        try:
            sort_field = filter_form.cleaned_data.get('p3_sort_field')
            sort_dir = filter_form.cleaned_data.get('p3_sort_dir')
        except AttributeError:
            sort_field = html.mark_safe(filter_form['p3_sort_field'].value())

    context = {'page': page,
               'type': code,
               'document_type': document_type,
               'document_types': document_types,
               'filter_form': filter_form,
               'search': search,
               'sort_field': sort_field,
               'sort_dir': sort_dir}
    return render(request, 'user/_list.html', context)


def add(user_func_class, id, code):
    uf = utils.get_class(user_func_class)()
    uf.user = User.objects.get(pk=id)
    uf.document_type = DocumentType.objects.get(code=code)
    uf.save()
    return redirect('user.edit', id=uf.pk, type=code)
