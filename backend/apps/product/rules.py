import json

import apps.product.api.temp
from apps.notification.utils import Notification
from apps.product.utils.utils import ProductUtils
from apps.user.models import User, UserHierarchy


class Rules:
    def __init__(self, calculation_object):
        self.product = calculation_object.product
        self.rules = calculation_object.product.document.type.financial_rules
        self.notifications = []
        self.calculation_object = calculation_object

    @staticmethod
    def _handle_conditional_operator(operator, a, b):
        if operator == '=':
            return a == b
        elif operator == '>':
            return a > b
        elif operator == '<':
            return a < b
        elif operator == '>=':
            return a >= b
        elif operator == '<=':
            return a <= b

    @staticmethod
    def _after_before(rule, dt, start_date, end_date):
        result = True
        if rule["after_before"] == 'AFTER':
            result = ((dt - start_date).days == int(rule["days"] or 0)) if start_date else False
        elif rule["after_before"] == 'BEFORE':
            result = ((end_date - dt).days == int(rule["days"] or 0)) if end_date else False

        return result

    @staticmethod
    def _days(rule, dt, start_date, end_date, data):
        days = False

        if rule["days"] is None:
            return True

        # check if there is a rule event incoming
        rule_event = data['RULE_EVENTS'][rule['what']] if 'RULE_EVENTS' in data and rule['what'] in data[
            'RULE_EVENTS'] else None

        if rule_event:
            return Rules._after_before(rule=rule, dt=dt, start_date=rule_event['due_date'],
                                       end_date=rule_event['due_date'])
        else:
            return Rules._after_before(rule=rule, dt=dt, start_date=start_date, end_date=end_date)

    def what(self, data):
        if self.rules['what'] == 'EACH_INSTALMENT':
            return True

    @staticmethod
    def _conditions(rule, data: list):
        if not rule['condition']:
            return True

        return Rules._handle_conditional_operator(rule["rule_conditional_operator"],
                                                  data[rule['condition']],
                                                  int(rule["rule_conditional_value"])
                                                  )

    def handle_rules(self, dt, data):
        from apps.product.calc import AUTO_STATUS_CHANGE
        if not self.rules:
            return

        # DEBUG
        import datetime
        if dt == datetime.datetime.strptime('2025-02-20', '%Y-%m-%d').date():
            pass
        # END DEBUG

        for rule in self.rules:
            forced_status_change = False

            if rule['fire_on_event'] == 'True':
                if rule['what'] not in data['RULE_EVENTS']:
                    continue

                forced_status_change = data['RULE_EVENTS'][rule['what']][
                    'forced_status_change'] if 'forced_status_change' in data['RULE_EVENTS'][rule['what']] else False

            days = Rules._days(rule=rule, dt=dt, start_date=data['SCHEDULE_CURRENT_DATE'],
                               end_date=data['SCHEDULE_NEXT_DATE'], data=data)
            condition = Rules._conditions(rule, data) if days else False

            status = True

            # trigger rules
            if days and condition:
                if AUTO_STATUS_CHANGE:
                    if rule["rule_status_change_from"] and rule["rule_status_change_to"]:
                        if self.product.status.pk == int(rule[
                                                             "rule_status_change_from"]):  # and  self.product.document.status.pk != int(i["rule_status_change_to"]):
                            ProductUtils.change_status(product=self.product,
                                                       status=rule["rule_status_change_to"],
                                                       user=User.objects.get(status='SYSTEM'),
                                                       effective_date=dt)
                        else:
                            status = False

                    elif rule["rule_status_change_to"] and forced_status_change:
                        ProductUtils.change_status(product=self.product,
                                                   status=rule["rule_status_change_to"],
                                                   user=User.objects.get(status='SYSTEM'),
                                                   effective_date=dt)

                if status and rule["rule_generate_alert_for"] and rule["rule_generate_alert_text"]:
                    user_list = []
                    for i in json.loads(rule["rule_generate_alert_for"]):
                        if i == '__RESPONSIBLE__':
                            user_list.append(self.product.document.responsible)
                        else:
                            user_list.extend([i.user for i in UserHierarchy.objects.filter(hierarchy=i)])

                    # create notification only when date equals today
                    # if dt == datetime.date.today():
                    Notification(user_list=user_list,
                                 template_code=None,  # todo: add template choosing functionality for
                                 document=self.product.document,
                                 text=rule["rule_generate_alert_text"],
                                 params=None,
                                 effective_date=dt
                                 ).register()

                if rule['rule_run_method']:
                    # run_method = rule['rule_run_method'].rsplit('.', 1)
                    # print('run_method[0]: ', run_method[0])
                    #
                    # module = utils.myimport(run_method[0])
                    # print('module', module)
                    # getattr(module, run_method[1])(self.calculation_object)
                    apps.product.api.temp.set_max_interest_for_delay(self.calculation_object)
