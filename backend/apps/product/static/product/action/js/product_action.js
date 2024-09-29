$(document).ready(function () {

    $("#report_preview_btn").click(function () {
        let data = {}; //JSON.stringify($('form#rd_form').serializeArray());
        $.each($('input[name^="rdf-"]'), function (i, e) {
            console.log($(e).prop('name'));
            data[$(e).prop('name')] = $(e).val();
        });

        data = JSON.stringify(data);
        $(".loader-container").fadeIn();


        $.ajax({
            url: '/product/action-report-preview/',
            method: "post",
            data: {formData: data, idAction: _globals.idAction, idProduct: _globals.idProduct, csrf_token: _globals.csrf_token},
            success: function (res) {
                if (res.output_file_name) {
                    $("#report_preview_container").html(`<embed type="application/pdf" src="/media/reports/tmp/${res.output_file_name + ".pdf"}" width="100%" height="100%"></embed>`);
                }
            },
            error: function (res) {
                console.log(res);
                let resp = res.responseJSON;
                let err = JSON.stringify(resp.errmsg);
                swal('Wystąpiły błędy', err, 'error');
            },
            complete: function () {
                $(".loader-container").fadeOut();
            }
        })
    })
});