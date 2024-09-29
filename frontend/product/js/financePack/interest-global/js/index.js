import InterestGlobal from "./interest-global";
import {SystemException} from "../../../../../_core/exception";
// import {Datepicker} from "../../../../../_core/controls/vanillajs-datepicker-3ws";
// import pl from "../../../../../_core/controls/vanillajs-datepicker-3ws/js/i18n/locales/pl"
//
// pl.pl.daysMin = ["Nd", "Pn", "Wt", "Śr", "Cz", "Pt", "So"];
// Object.assign(Datepicker.locales, pl);

document.addEventListener('DOMContentLoaded', () => {

    let interestGlobal = new InterestGlobal(
        document.getElementById('interestGlobalListContainer'),
        document.getElementById('interestGlobalFormContainer'),
        document.getElementById('interestGlobalFormTemplate')
    );


    document.querySelector('.add-global-interest-btn').addEventListener('click', () => {
        interestGlobal.form.show(true, true);
    });

    document.querySelector('.delete-global-interest-btn').addEventListener('click', (evt) => {
        Alert.questionWarning(
            'Czy na pewno usunąć wpis?',
            '',
            () => {
                InterestGlobal.delete(evt.target.closest('tr').dataset['id']).then(() => {
                        console.log('global interest deleted');
                        window.location.reload()
                    },
                    (resp) => {
                        throw new SystemException(resp)
                    }
                )
            });
    });

});

