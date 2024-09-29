function addRowEntry() {
    "use strict";
    let lovList = $("#attribute_lov_table").find("tbody");
    let row = $('#lov_formset_form_template').html();
    // let row =
    //     '<tr data-status="NEW">' +
    //     '<td><input class="form-control input-sm lov-value" type="text" name="lov_value"/></td>' +
    //     '<td><input class="form-control input-sm lov-label" type="text" name="lov_label"/></td>' +
    //     '<td><a class="btn btn-danger btn-sm delete-lov-entry"><i class="fa fa-trash-alt"></i></a></td>' +
    //     '</tr>';
    lovList.append(row);
}

function deleteRowEntry(el) {
    el.closest('tr').remove();
}

function hideRowEntry(el) {
    "use strict";
}

// function populateLov() {
//     "use strict";
//     let lovVal = $("#id_lov").val();
//
//     if (!lovVal) {
//         return
//     }
//     let lovValJson = $.parseJSON(lovVal);
//     if (!lovValJson) {
//         return;
//     }
//
//     let lovRowContainer = $("#lov_row_container");
//
//     if (lovValJson.data) {
//         let row = '';
//         console.log(lovValJson.data);
//         $.each(lovValJson.data, function (i, e) {
//             Object.keys(e).forEach(function (key) {
//                 row =
//                     '<tr>' +
//                     `<td><input class="form-control input-sm lov-label" type="text" name="lov_value" value="${key}" readonly="readonly"/></td>` +
//                     `<td><input class="form-control input-sm lov-label" type="text" name="lov_label" value="${e[key]}"/></td>` +
//                     '<td></td>' +
//                     '</tr>';
//             });
//             lovRowContainer.append(row);
//         });
//     }
//     if (lovValJson.nullvalue) {
//         $("#lov_nullvalue").prop('checked', true);
//     }
// }

// function validateLov() {
//     "use strict";
//     let valid = true;
//     let matches = [];
//     let errors = [];
//     let lovRows = $("#lov_row_container").find('tr');
//     lovRows.each(function (i, e) {
//         let _e = $(e);
//         let val = _e.find('input[name="lov_value"]').val();
//         if ($.inArray(val, matches) === -1) {
//             matches.push(val);
//         }
//         else {
//             errors.push(`zdublowany kod: ${val}; rekord: ${i + 1}`);
//         }
//     });
//     return errors;
// }

// function jsonifyLovList() {
//     "use strict";
//
//     let lov = $('#id_lov');
//     let lovRows = $("#lov_row_container").find('tr');
//     if (!lovRows.length) {
//         lov.val(null);
//         return;
//     }
//
//     let lovJson = {};
//     let data = [];
//
//     lovRows.each(function (i, e) {
//         let _e = $(e);
//         let dict = {};
//         let value = _e.find('input[name="lov_value"]').val().toUpperCase();
//         let label = _e.find('input[name="lov_label"]').val();
//         dict[value] = label;
//         data.push(dict);
//     });
//
//     lovJson['data'] = data;
//     lovJson['nullvalue'] = $("#lov_nullvalue").is(":checked");
//     lov.val(JSON.stringify(lovJson));
// }

function fixLovFormset() {
    "use strict";
    let cnt = 0;
    let lovRows = $("#lov_row_container").find('tr');

    $.each(lovRows, function (i, e) {
        $.each($(e).find('input, select, textarea'), function () {
            let name = $(this).attr('name').replace(/__prefix__/g, cnt);
            $(this).attr('name', name);
        });
        cnt++;
    });
    $('#id_lov-TOTAL_FORMS').val(cnt);
}


$(document).ready(function () {
    $("#add_lov_entry_btn").click(function () {
        addRowEntry();
    });

    $(document).on('click', '.hide-low-entry', function () {
        let _this = $(this);
        swal({
            title: 'Czy na pewno ukryć wpis?',
            text: '',
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Tak, ukryj!",
            cancelButtonText: "Nie!",
            closeOnConfirm: true
        }, function () {
            "use strict";
            hideRowEntry(_this);
        });
    });

    $(document).on('click', '.delete-lov-entry', function () {
        let _this = $(this);
        swal({
            title: 'Czy na pewno usunąć wpis?',
            text: '',
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Tak, usuń!",
            cancelButtonText: "Nie!",
            closeOnConfirm: true
        }, function () {
            "use strict";
            deleteRowEntry(_this);
        });
    });

    $(".btn-submit-form").click(function () {
        fixLovFormset();
        $('form').submit();
    });

    // populateLov();


});