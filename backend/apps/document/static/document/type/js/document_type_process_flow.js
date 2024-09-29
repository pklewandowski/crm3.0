function DocumentTypeProcessFlow(type) {
    this.type = type;
    this.getStatusFlow = function (code) {
        $.ajax({
            url: '/document/type/get-status-flow/',
            method: 'POST',
            data: {type: this.type, code: code}
        }).done(function (res) {
            console.log(res.data);
            if (!res.data.length) {
                $("#av_hierarchy").html(null).closest('div.form-group').hide();
                $("#id_document-hierarchy").val(null);
                return;
            }
            let row = '';
            $.each(res.data, function (i, e) {
                row += '<option value="' + e.value + '">' + e.label + '</option>';
            });
            $('#av_hierarchy').html(row).closest('div.form-group').show();
            $("#id_document-hierarchy").val($('#av_hierarchy').val());

        }).fail(function (res) {
            swal(res.responseJSON.errmsg, '', 'error');
        });
    }
}
