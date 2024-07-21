import collections
import datetime
import json
import traceback

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from apps.stat.summary_report.base import StatBase, StatException
from apps.stat.summary_report.forms import IncomeForm, StatGroupAdviserForm, StatGroupLoanStatusForm, AdviserRankForm, DynamicsForm
from apps.stat.summary_report.models import StatGroupAdviser, StatGroupLoanStatus
from apps.stat.summary_report.utils.adviser_rank import AdviserRank
from apps.stat.summary_report.utils.dynamics import Dynamics
from apps.stat.summary_report.utils.income import Income
from apps.user_func.adviser.models import Adviser


class Index(StatBase):
    def set_app_name(self):
        self._app_name = 'stat'

    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def dispatch(self, request, *args, **kwargs):
        context = {
            'income': {
                'form': IncomeForm(request.POST or None,
                                   prefix='income',
                                   initial={'date_from': "%s-%s-01" % (datetime.date.today().year if datetime.date.today().month - 3 else datetime.date.today().year - 1,
                                                                       datetime.date.today().month - 3 or 10)}
                                   )
            },
            'adviserRank': {
                'form': AdviserRankForm(request.POST or None,
                                        prefix='adviser_rank',
                                        initial={'date_from': "%s-%s-01" % (datetime.date.today().year, datetime.date.today().month)}
                                        )
            },

            'dynamics': {
                'form': DynamicsForm(
                    request.POST or None,
                    prefix='dynamics',
                    initial={
                        'date_1': "%s-%s-01" % (datetime.date.today().year, datetime.date.today().month),
                        'date_2': "%s-%s-01" % (datetime.date.today().year if datetime.date.today().month - 2 else datetime.date.today().year - 1,
                                                datetime.date.today().month - 1 or 12),
                        'date_3': "%s-%s-01" % (datetime.date.today().year if datetime.date.today().month - 3 else datetime.date.today().year - 2,
                                                datetime.date.today().month - 2 or 11)
                    }
                )
            }
        }

        return render(request, 'stat/index.html', context=context)


def get_data(request):
    status = 200
    response_data = {}
    data = {}

    data_type = request.POST.get('dataType', '__all__')

    try:
        if data_type in ['__all__', 'income']:
            income_form = IncomeForm(request.POST or None, prefix='income')
            if income_form.is_valid():
                advisers = [i.pk for i in income_form.cleaned_data.get('adviser')]
                for i in income_form.cleaned_data.get('drs'):
                    advisers.extend(i.advisers)

                advisers = ','.join(list(map(lambda x: '\'%s\'' % x, advisers)))
                brokers = ','.join(list(map(lambda x: '\'%s\'' % x, [i.pk for i in income_form.cleaned_data.get('broker')])))
                agreement_type = ','.join(list(map(lambda x: '\'%s\'' % x, income_form.cleaned_data.get('agreement_type'))))

                loan_status = income_form.cleaned_data.get('status')
                group_loan_status = income_form.cleaned_data.get('group_status')
                all_statuses = []

                if status:
                    for i in loan_status:
                        all_statuses.append(i.pk)

                if group_loan_status:
                    for i in group_loan_status:
                        all_statuses.extend(i.statuses)

                if all_statuses:
                    # remove duplicates and then convert to comma delimited string
                    all_statuses = ','.join(map(lambda x: str(x), list(dict.fromkeys(all_statuses))))

                data['income'] = Income.get_pivot_data(
                    date_from=income_form.cleaned_data.get('date_from'),
                    date_to=income_form.cleaned_data.get('date_to'),
                    advisers=advisers,
                    brokers=brokers,
                    status=all_statuses or None,
                    agreement_type=agreement_type or None,
                    business_type=income_form.cleaned_data.get('business_type'),
                )

        if data_type in ['__all__', 'adviserRank']:
            adviser_rank_form = AdviserRankForm(request.POST or None, prefix='adviser_rank')
            advisers = ''
            if adviser_rank_form.is_valid():
                for i in adviser_rank_form.cleaned_data.get('adviser'):
                    advisers += "'%s'," % i.pk

                advisers = advisers[:-1]
                date_from = adviser_rank_form.cleaned_data.get('date_from')
                date_to = adviser_rank_form.cleaned_data.get('date_to')

                data['adviserRank'] = AdviserRank.get_data(date_from=date_from, date_to=date_to, advisers=advisers)

        if data_type in ['__all__', 'dynamics']:
            data['dynamics'] = {}
            dynamics_form = DynamicsForm(request.POST or None, prefix='dynamics')
            today = datetime.date.today()

            if dynamics_form.is_valid():
                all_statuses = []
                for i in dynamics_form.cleaned_data.get('group_status'):
                    all_statuses.extend(i.statuses)

                data['dynamics'] = Dynamics.get_data(
                    date_1=dynamics_form.cleaned_data.get('date_1', today.isoformat()),
                    date_2=dynamics_form.cleaned_data.get('date_2', today.isoformat()),
                    date_3=dynamics_form.cleaned_data.get('date_3', today.isoformat()),
                    status=','.join(map(lambda x: str(x), list(dict.fromkeys(all_statuses))))
                )

        response_data = data

    except Exception as ex:
        status = 400
        response_data['errmsg'] = "%s %s %s" % (str(ex), '\n', traceback.format_exc() or '')

    return HttpResponse(json.dumps(response_data), status=status, content_type="application/json")


def get_pivot_data(request):
    status = 200
    response_data = {}

    try:
        response_data['data'] = Income.get_pivot_data()

    except Exception as ex:
        status = 400
        response_data['errmsg'] = "%s %s %s" % (str(ex), '\n', traceback.format_exc() or '')

    return HttpResponse(json.dumps(response_data), status=status, content_type="application/json")


def get_adviser_rank_data(request):
    status = 200
    response_data = {}

    advisers = ''
    date_from = None
    date_to = None

    form = AdviserRankForm(request.POST or None, prefix='adviser_rank')

    if form.is_valid():
        for i in form.cleaned_data.get('adviser'):
            advisers += "'%s'," % i.pk

        advisers = advisers[:-1]
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

    try:
        response_data = {
            'adviser_rank': AdviserRank.get_data(date_from=date_from, date_to=date_to, advisers=advisers)
        }
    except Exception as ex:
        status = 400
        response_data['errmsg'] = "%s %s %s" % (str(ex), '\n', traceback.format_exc() or '')

    return HttpResponse(json.dumps(response_data), status=status, content_type="application/json")


class AddGroupAdviser(StatBase):
    def set_app_name(self):
        self._app_name = 'stat'

    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def dispatch(self, request, *args, **kwargs):

        form = StatGroupAdviserForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                StatGroupAdviser.objects.create(
                    name=form.cleaned_data.get('name'),
                    advisers=[i.pk for i in form.cleaned_data.get('adviser_list')]
                )
                return redirect('stat.index')

        return render(request, 'stat/group/adviser/add.html', context={'form': form})


class EditGroupAdviser(StatBase):
    def set_app_name(self):
        self._app_name = 'stat'

    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def dispatch(self, request, *args, **kwargs):
        id = self.kwargs['id']

        if not id:
            raise Exception('Brak ID grupy do edycji')

        stat_group_adviser = StatGroupAdviser.objects.get(pk=id)

        form = StatGroupAdviserForm(
            request.POST or None,
            instance=stat_group_adviser,
            initial={'adviser_list': stat_group_adviser.advisers}
        )

        if request.method == 'POST':
            if form.is_valid() and form.has_changed():
                stat_group_adviser.advisers = [i.pk for i in form.cleaned_data.get('adviser_list')]
                stat_group_adviser.name = form.cleaned_data.get('name')
                stat_group_adviser.save()

                return redirect('stat.index')

        return render(request, 'stat/group/adviser/add.html', context={'form': form})


class DeleteGroupAdviser(StatBase):
    def set_app_name(self):
        self._app_name = 'stat'

    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def dispatch(self, request, *args, **kwargs):
        response_data = {}
        status = 200
        id = request.POST.get('id')

        StatGroupAdviser.objects.get(pk=id).delete()

        try:
            if not id:
                raise StatException('Brak ID grupy')
        except Exception as ex:
            response_data['errmsg'] = str(ex)
            status = 400

        return HttpResponse(json.dumps(response_data), content_type='application/json', status=status)


class AddGroupLoanStatus(StatBase):
    def set_app_name(self):
        self._app_name = 'stat'

    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def dispatch(self, request, *args, **kwargs):

        form = StatGroupLoanStatusForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                StatGroupLoanStatus.objects.create(
                    name=form.cleaned_data.get('name'),
                    statuses=[i.pk for i in form.cleaned_data.get('status_list')]
                )
                return redirect('stat.index')

        return render(request, 'stat/group/loan_status/add.html', context={'form': form})


class EditGroupLoanStatus(StatBase):
    def set_app_name(self):
        self._app_name = 'stat'

    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def dispatch(self, request, *args, **kwargs):
        id = self.kwargs['id']

        if not id:
            raise Exception('Brak ID grupy do edycji')

        stat_group_loan_status = StatGroupLoanStatus.objects.get(pk=id)

        form = StatGroupLoanStatusForm(
            request.POST or None,
            instance=stat_group_loan_status,
            initial={'status_list': stat_group_loan_status.statuses}
        )

        if request.method == 'POST':
            if form.is_valid() and form.has_changed():
                stat_group_loan_status.statuses = [i.pk for i in form.cleaned_data.get('status_list')]
                stat_group_loan_status.name = form.cleaned_data.get('name')
                stat_group_loan_status.save()

                return redirect('stat.index')

        return render(request, 'stat/group/loan_status/add.html', context={'form': form})


class DeleteGroupLoanStatus(StatBase):
    def set_app_name(self):
        self._app_name = 'stat'

    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def dispatch(self, request, *args, **kwargs):
        response_data = {}
        status = 200
        id = request.POST.get('id')

        StatGroupLoanStatus.objects.get(pk=id).delete()

        try:
            if not id:
                raise StatException('Brak ID grupy')
        except Exception as ex:
            response_data['errmsg'] = str(ex)
            status = 400

        return HttpResponse(json.dumps(response_data), content_type='application/json', status=status)
