//var frameSrc = add_attribute_url;
//
//$('#openBtn').click(function(){
//    $('#myModal').on('show', function () {
//
//        $('iframe').attr("src",frameSrc);
//
//	});
//    $('#myModal').modal({show:true})


$("#product-type-cashflow-formset-table tbody").sortable({
    stop: function () {
        $.each($("#product-type-cashflow-formset-table tbody tr"), function (i, e) {
            $(this).find($("input.accounting-order")).val(i + 1);
        });
    }

});
