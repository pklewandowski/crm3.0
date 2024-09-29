if ($("#{{ form.is_local.id_for_label }}").prop("checked")) {

    $("#meeting-room-address-panel fieldset").attr('disabled', true);
} else {
    $("#meeting-room-address-panel fieldset").removeAttr('disabled');
}

$(".btn-submit").click(function () {
    $("form#user-form").submit();
});

$("#{{ form.is_local.id_for_label }}").change(function () {

    if ($("#{{ form.is_local.id_for_label }}").prop("checked")) {

        $("#meeting-room-address-panel fieldset").attr('disabled', true);
    } else {
        $("#meeting-room-address-panel fieldset").removeAttr('disabled');
    }
});
