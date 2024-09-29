function get_accounting_ordered_choosen() {
    var choosen = [];
    $.each($("#id_accounting_ordered_choosen_list li"), function (i, e) {
        choosen.push($(e).data('id'));
    });

    $('#id_accounting_ordered').val(choosen.join(","));
}

