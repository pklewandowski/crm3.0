#!/bin/bash

# job for performing daily calculations on active loans
# with no required_calculation_date and recount_required_date_creation_marker set
# script should run every day at 01 hour minutes: 0 1 * * *
cd "$TWS_LOAN_APP_ROOT" || exit
"$TWS_LOAN_APP_VENV_ROOT"python ./manage.py calculate_products_daily