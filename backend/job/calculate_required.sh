#!/bin/bash

# job for calculating loans that have to be calculated due to any changes.
# the loan products have set required_calculation_date and recount_required_date_creation_marker values
# script should run every 10 minutes: */10 * * * *
cd "$TWS_LOAN_APP_ROOT" || exit
"$TWS_LOAN_APP_VENV_ROOT"python ./manage.py calculate_required