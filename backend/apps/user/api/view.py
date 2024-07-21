import os
import traceback
import uuid

from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

import apps.user.utils as user_utils
import crm_settings
from application.wrapper import rest_api_wrapper
from apps.attachment import utils as atm_utils
from apps.attachment.models import Attachment
from apps.message.models import MessageTemplate
from apps.message.utils import register_message
from apps.user.models import User, UserAttachment, UserRelation
from apps.user_func.client.models import ClientAccessToken, Client
from .serializers import UserSerializer, UserAttachmentSerializer, UserRelationSerializer
from .services import services
from ..forms import UserRelationForm
from ...user_func.employee.models import Employee


class UserException(Exception):
    pass


class UserView(APIView):
    def get(self, request):
        serializer = UserSerializer(User.objects.get(pk=request.query_params.get('id')))
        return Response(serializer.data)


class UserRelationApi(APIView):
    def get(self, request):
        response_status = status.HTTP_200_OK

        try:
            user_id = request.query_params.get('userId', None)
            if not user_id:
                raise UserException('[{}][get]: {}'.format(self.__class__.__name__, _('Brak id użytkownika')))
            response_data = {"left": UserRelationSerializer(UserRelation.objects.filter(left=User.objects.get(pk=user_id)), many=True).data,
                             "right": UserRelationSerializer(UserRelation.objects.filter(right=User.objects.get(pk=user_id)), many=True).data
                             }

        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data = {"errmsg": str(ex), "traceback": traceback.format_exc()}

        return Response(data=response_data, status=response_status)

    def post(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}
        form = None

        try:
            form = UserRelationForm(data=request.data, prefix='userrelation')
            if form.is_valid():
                form.save()
            else:
                raise UserException('Wystąpiły błędy w formularzu')

        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data = {"errmsg": str(ex), "traceback": traceback.format_exc(), 'errors': form.errors if form else '', 'form_prefix': form.prefix}

        return Response(data=response_data, status=response_status)

    def put(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}
        form = None
        try:
            form = UserRelationForm(data=request.data, instance=UserRelation.objects.get(pk=request.data.get('userRelationId')))
            if form.has_changed() and form.is_valid():
                form.save()
        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data = {"errmsg": str(ex), "traceback": traceback.format_exc(), 'errors': form.errors if form else '', 'form_prefix': form.prefix}

        return Response(data=response_data, status=response_status)

    def delete(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}
        try:
            relation_id = request.data.get('relationId', None)
            if not relation_id:
                raise UserException('[{}][delete]: {}'.format(self.__class__.__name__, _('Brak id relacji do usunięcia')))
            UserRelation.objects.get(pk=relation_id).delete()

        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data = {"errmsg": str(ex), "traceback": traceback.format_exc()}

        return Response(data=response_data, status=response_status)


class AttachmentApi(APIView):
    @staticmethod
    def _save_attachment(**kwargs):
        parent_id = kwargs.get('parent_id')

        attachment = Attachment.create(
            file_name=kwargs.get('file_name'),
            file_ext=kwargs.get('file_ext'),
            file_mime_type=kwargs.get('file_mime_type'),
            file_path=kwargs.get('file_path'),
            file_original_name=kwargs.get('file_original_name'),
            attachment_type='file',
            created_by_username=kwargs.get('created_by_username')
        )

        da = UserAttachment.objects.create(
            document=kwargs.get('document'),
            attachment=attachment,
            created_by=kwargs.get('user'),
            parent=UserAttachment.objects.get(pk=parent_id) if parent_id else None
        )
        return da

    def get(self, request):
        document = User.objects.get(pk=request.query_params.get('id'))
        parent = UserAttachment.objects.get(pk=request.query_params.get('parent')) if request.query_params.get('parent') else None

        q = UserAttachment.objects.filter(document=document, parent=parent).order_by('-is_dir', 'name', 'attachment__file_original_name')
        serializer = UserAttachmentSerializer(q, many=True)

        return Response(serializer.data)

    def post(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}

        try:
            response_data['saved_files'] = atm_utils.save_attachments(request=request,
                                                                      api={
                                                                          'path': 'user/attachments/',
                                                                          'store_class': User,
                                                                          'save_fn': AttachmentApi._save_attachment,  # getattr(AttachmentApi, '_save_attachment'),
                                                                          'serializer': UserAttachmentSerializer
                                                                      })
        except Exception as e:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data = {'errmsg': str(e), "traceback": traceback.format_exc()}

        return Response(response_data, status=response_status)

    def delete(self, request):
        try:
            with transaction.atomic():
                attachment = Attachment.objects.get(pk=request.data.get('attachmentId'))
                user = User.objects.get(pk=request.data.get('documentId'))

                # No need to delete DocumentAttachment record due to on_delete.CASCADE entry in model
                # DocumentAttachment.objects.get(attachment=attachment, document=document).delete()
                attachment.delete()

                path = os.path.join(crm_settings.MEDIA_ROOT, 'user', str(user.pk), attachment.file_name)
                if os.path.exists(path):
                    os.remove(path)

                return Response(data={})

        except Exception as e:
            return Response(data={'errmsg': str(e), 'traceback': traceback.format_exc()}, exception=True, status=status.HTTP_400_BAD_REQUEST)


class AgreementApi(APIView):
    # get users' confirmed agreements
    def get(self, request):
        pass

    def post(self, request):
        response_data = {}
        response_status = status.HTTP_200_OK
        try:
            client = Client.objects.get(pk=request.data.get('userId'))
            if not client.user.email:
                raise Exception('Klient nie posiada wprowadzonego adresu e-mail')

            token = str(uuid.uuid4())
            ClientAccessToken.objects.create(client=client, token=token, valid=True)

            message_template = MessageTemplate.objects.get(code='AGREEMENT_REQUEST')
            register_message(
                template=message_template,
                source={'user': client.user},
                add_params={'AUTH_TOKEN': token},
                recipients=[client.user.email]
            )

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(response_data, response_status)


class PasswordReset(APIView):
    @rest_api_wrapper
    def post(self, request):
        username = request.data.get('username')

        if not username:
            raise UserException('pole login musi być wypełniopne')

        q = (
                Q(user__username=username) |
                Q(user__email=username) |
                Q(user__personal_id=username) |
                Q(user__nip=username)
        )

        try:
            user = Employee.objects.get(q).user
        except User.MultipleObjectsReturned:
            raise UserException('Zbyt wiele pasujących pracowników dla loginu: %s' % username)
        except User.DoesNotExist:
            raise UserException('Nie znaleziono pracownika dla loginu: %s' % username)

        password = user_utils.generate_password()

        user.initial_password = password
        user.set_password(password)
        user.password_valid = False
        user.save()

        if user.email:
            register_message(
                template=MessageTemplate.objects.get(code='PASSWORD_RESET'),
                recipients=[user.email],
                source={'user': user},
                send_immediately=True
            )
            response_data = {'email': 'OK'}
        else:
            response_data = {'password': password}

        return response_data


class UserNote(APIView):
    def post(self, request):
        response_data = {}
        response_status = status.HTTP_200_OK
        note_text = request.data.get('text')
        note_user = User.objects.get(pk=request.data.get('id'))

        try:
            if not note_text:
                raise Exception('note has no text!')
            response_data = services.UserServices(request.user).save_note(note_text=note_text, note_user=note_user)

        except Exception as ex:
            response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
        return Response(response_data, response_status)


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def get_for_select2(request):
    response_data = {}
    response_status = status.HTTP_200_OK

    id = request.GET.get('id', None)
    exclude = request.GET.get('exclude', [])
    key = request.GET.get('q')

    try:
        if id:
            q = Q(pk=id)
        else:
            q = (
                    Q(first_name__icontains=key) |
                    Q(last_name__icontains=key) |
                    Q(company_name__icontains=key) |
                    Q(nip__icontains=key) |
                    Q(regon__icontains=key) |
                    Q(krs__icontains=key) |
                    Q(personal_id__icontains=key) |
                    Q(phone_one__icontains=key) |
                    Q(email__icontains=key)
            )
        if exclude:
            pass

        result = User.objects.filter(q)
        # if users.count() > 500:
        #     response_data['results'] = []
        # else:
        response_data['results'] = [
            {
                'id': i.pk,
                'text': (i.company_name + ' ' if i.company_name else '') +
                        ((i.first_name + ' ' if i.first_name else '') + (i.last_name or '')),
                'firstName': i.first_name,
                'lastName': i.last_name
            } for i in result]

    except Exception as e:
        response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data['errmsg'] = str(e)
        response_data['traceback'] = traceback.format_exc()

    return Response(response_data, status=response_status)


class UserDetails(APIView):
    @rest_api_wrapper
    def get(self, request):
        return services.get_details(request=request)


