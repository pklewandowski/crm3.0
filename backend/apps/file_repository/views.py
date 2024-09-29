import os

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import ListView

from apps.file_repository import REPORT_REPO_DIR
from apps.file_repository.api.serializers import FileRepositorySerializer
from apps.file_repository.models import FileRepository


class FileRepositoryListView(ListView):
    model = FileRepository
    paginate_by = 2
    ordering = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['serializer'] = FileRepositorySerializer()
        context['style'] = {'template_pack': 'rest_framework/vertical/'}
        return context


def get_file(request, id):
    # todo: finally create global file repository management and use it to get files
    report = FileRepository.objects.get(pk=id)
    with open(os.path.join(settings.MEDIA_ROOT, REPORT_REPO_DIR, report.filename), 'r+b') as f:
        response = HttpResponse(f.read(), content_type='%s; %s' % (report.mimetype, 'charset=utf-8'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % report.original_filename.encode('ascii',
                                                                                                        'replace').decode()
        f.close()
        return response
