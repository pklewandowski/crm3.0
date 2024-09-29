# wymagane dla indywidualnego usrea
USER_TYPE_REQUIRED_FIELDS = {'EMPLOYEE': ['first_name', 'last_name', 'email', 'phone_one'],
                             'ADVISER': ['first_name', 'last_name', 'email', 'phone_one', 'personal_id'],
                             'BROKER': ['first_name', 'last_name', 'email', 'phone_one'],
                             'CLIENT': ['last_name'],
                             'LAWOFFICE': ['last_name'],
                             'CONTRACTOR': ['last_name']

                             }
# wymagalne, gdy user jest firma
USER_TYPE_COMPANY_REQUIRED_FIELDS = {'EMPLOYEE': ['company_name', 'email', 'phone_one'],
                                     'ADVISER': ['company_name', 'email', 'phone_one', 'nip'],
                                     'BROKER': ['company_name', 'email', 'phone_one', 'nip'],
                                     'CLIENT': ['company_name'],
                                     'LAWOFFICE': ['company_name'],
                                     'CONTRACTOR': ['company_name']
                                     }
