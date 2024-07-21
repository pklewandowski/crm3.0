$(document).ready(function () {

    $("#id_schedule-employee_").select2({
        theme: 'bootstrap',
        ajax: {
            method: 'post',
            url: '/schedule/get-employees-for-meeting-filter/', //TODO: DRUT! Wziąć docelowo ze zmiennej globalnej ustqawionej przez {% static... %}
            dataType: 'json'
        },
        minimumInputLength: 2,
        language: "pl",
        width: '100%'
    });

    $("#id_schedule-client_").select2({
        theme: 'bootstrap',
        ajax: {
            method: 'post',
            url: '/schedule/get-clients-for-meeting-filter/', //TODO: DRUT! Wziąć docelowo ze zmiennej globalnej ustqawionej przez {% static... %}
            dataType: 'json',
            data: function (params) {
                "use strict";
                return {
                    search: params.term,
                    idEmployee: $("#id_schedule-employee_").val()
                }
            }
        },
        minimumInputLength: 2,
        language: "pl",
        width: '100%'
    });

    if (mode === 'advanced') {
        $("#id_schedule-host_user_").select2({
            theme: 'bootstrap',
            ajax: {
                method: 'post',
                url: '/schedule/get-employees-for-meeting-filter/', //TODO: DRUT! Wziąć docelowo ze zmiennej globalnej ustqawionej przez {% static... %}
                dataType: 'json'
            },
            minimumInputLength: 2,
            language: "pl",
            width: '100%'
        });
    }

    if (mode === 'advanced') {
        $("#id_schedule-single_person_").select2({
            theme: 'bootstrap',
            ajax: {
                method: 'post',
                url: '/schedule/get-employees-for-meeting-filter/', //TODO: DRUT! Wziąć docelowo ze zmiennej globalnej ustqawionej przez {% static... %}
                dataType: 'json'
            },
            minimumInputLength: 2,
            language: "pl",
            width: '100%'
        });
    }
});