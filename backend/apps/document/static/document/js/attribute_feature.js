$(document).ready(function () {
    $(".select-all").change(function () {

        // swal({
        //     text: "Czy na pewno zaznaczyć wszystkie?",
        //
        // });

        if ($(this).is(':checked')) {
            $('input[data-section="' +
                $(this).data('section') + '"][data-status="' +
                $(this).data('status') + '"][data-feature="' +
                $(this).data('feature') + '"]').prop('checked', true);

        } else {
            $('input[data-section="' +
                $(this).data('section') + '"][data-status="' +
                $(this).data('status') + '"][data-feature="' +
                $(this).data('feature') + '"]').prop('checked', false);
        }
    });
});