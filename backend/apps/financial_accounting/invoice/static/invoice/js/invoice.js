function deleteFormsetRow(e, msg) {

    var that = e;

    swal({
        title: 'Jesteś pewien?',
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: "Tak, usuń!",
        confirmButtonColor: "#DD6B55",
        cancelButtonText: "Nie",
        closeOnConfirm: true
    }, function () {
        that.parents('tr').remove();
    });
}


$(document).ready(function () {

    var documentProcessFlow = new DocumentTypeProcessFlow(documentType);
    console.log(documentProcessFlow);
    $(document).on('click', "#add_invoice_item_btn", function () {

        var form_idx = $('table#invoice_item_table tbody tr').length;
        var row = $("#invoice_item_row_template").html();

        row = row.replace(/__prefix__/g, form_idx);
        row = row.replace(/__INVOICE_ID__/g, invoiceId);
        $('#id_invoiceitem-TOTAL_FORMS').val(form_idx + 1);

        $("#invoice_item_table tbody").append(row);
    });

    $(document).on('click', "#add_invoice_extra_item_btn", function () {

        var form_idx = $('table#invoice_extra_item_table tbody tr').length;
        var row = $("#invoice_extra_item_row_template").html();

        row = row.replace(/__prefix__/g, form_idx);
        row = row.replace(/__INVOICE_ID__/g, invoiceId);

        $('#id_invoiceextraitem-TOTAL_FORMS').val(form_idx + 1);
        $("#invoice_extra_item_table tbody").append(row);
    });

    $(document).on('click', '#invoice_item_container  tbody  tr a.delete', function () {
        deleteFormsetRow($(this), 'Tak, usuń z listy!');
    });

    $(document).on('click', '#invoice_extra_item_container  tbody  tr a.delete', function () {
        deleteFormsetRow($(this), 'Tak, usuń z listy!');
    });

    $(document).on('click', '.scan-thumbnail', function () {
        var src = $(this).find('img').attr('src');
        $('#image_preview').attr('src', src);
        $('#image_preview_modal').modal();
    });

    $(document).on('click', '.prtscn-thumbnail', function () {
        var src = $(this).find('img').attr('src');
        $('#image_preview').attr('src', src);
        $('#image_preview_modal').modal();
    });

    /*TODO: docelowo KONIECZNIE przenieść obsługę do document*/
    $("#id_document-status_flow").change(function () {
        documentProcessFlow.getStatusFlow($(this).val());
    });

    $("#av_hierarchy").change(function(){
        $("#id_document-hierarchy").val($(this).val());
    });
});
