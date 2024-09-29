
$(document).ready(function () {
    $("#id_accounting_available_list, #id_accounting_ordered_choosen_list").sortable({
        connectWith: ".connected-cashflow"
    }).disableSelection();

    $('form').on('submit', function (e) {
        get_accounting_ordered_choosen();
        //return false;
    });
});
