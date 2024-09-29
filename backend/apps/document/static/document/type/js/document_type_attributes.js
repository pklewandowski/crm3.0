$(document).ready(function () {

    $('.sortable-attributes').sortable({
        handle: ".fa-arrows-alt-v"
    });

    $('.sortable-items').sortable({
        connectWith: '.sortable-items',
        handle: ".fa-arrows-alt-v"
    });

    $('.sortable-attributes').disableSelection();
    $('.sortable-items').disableSelection();


    // $('.section-name').click(function () {
    //     $(this).parents('td').find('.attributes-list-table').toggle('slow');
    // });
    $('.section-name').click(function () {
        $(this).parents('td').find('.section-content').toggle(200);
    });

    $(".sortable-attributes").on("sortupdate", function (event, ui) {

        $.each($(this).find('div.document-type-section'), function (i) {
            $(this).children('.sq-input').val(i + 1);

        });

        $.each($(this).find('.attributes-list-table'), function (i) {

            let section_id = $(this).parents('.section-id').data('section-id');
            let column_id = $(this).data('column_id');

            $(this).find('input.attribute-section-id').val(section_id);
            $(this).find('input.attribute-section-column-id').val(column_id);

            $.each($(this).find('input.sq-input'), function (i) {
                $(this).val(i + 1);
            });
        });
    });

    $('.delete-attribute').click(function () {
        swal('Usuwanie zablokowane!', '', 'warning');
        return;

        that = $(this);

        swal({
            title: 'Czy na pewno kontynuować?',
            text: 'UWAGA: Usunięcie atrybutu skutkuje dla wszystkich dokumentów, które go posiadają!',
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Tak, usuń!",
            cancelButtonText: "Nie, zamknij!",
            closeOnConfirm: false
        }, function () {

            row = that.closest('tr');
            console.log(row);
            id = row.data('id');

            $.ajax({
                method: "POST",
                url: window.delete_attribute_url,
                data: {'id': id, 'csrfmiddlewaretoken': window.csrf_token},
                beforeSend: function () {
                    //$("#search-box").css("background","#FFF url(LoaderIcon.gif) no-repeat 165px");
                },
                success: function () {
                    swal('Atrybut został usunięty', '', 'success');
                    row.remove();
                },
                error: function() {
                    swal('Atrybut został usunięty', '', 'error');
                }
            })
        })
    });


    $('.delete-section').click(function () {

        swal('Usuwanie zablokowane!', '', 'warning');
        return;

        that = $(this);

        swal({
            title: 'Czy na pewno kontynuować?',
            text: 'UWAGA: Usunięcie sekcji skutkuje dla wszystkich produktów które ją posiadają!',
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Tak, usuń!",
            cancelButtonText: "Nie, zamknij!",
            closeOnConfirm: false
        }, function () {

            row = that.closest('tr');
            console.log(row);
            id = row.data('section-id');

            $.ajax({
                method: "POST",
                url: window.delete_section_url,
                data: {'id': id, 'csrfmiddlewaretoken': window.csrf_token},
                beforeSend: function () {
                    //$("#search-box").css("background","#FFF url(LoaderIcon.gif) no-repeat 165px");
                },
                success: function () {
                    swal('Sekcja została usunięta', '', 'success');
                    row.remove();
                },
                error: function() {
                    swal('Atrybut został usunięty', '', 'error');
                }
            })
        })
    });
});

