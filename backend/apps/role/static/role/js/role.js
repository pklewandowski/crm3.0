function roleFormReset() {
    $('form#role-form')[0].reset();
    $.each($("form#role-form textarea"), function () {
        $(this).text(null);
    });

    $.each($('form#role-form input[name="privs"]'), function(){
        $(this).prop('checked', false);
    });
}

$(document).ready(function () {

    $('#userListModal').modal({
        keyboard: false,
        backdrop: 'static',
        show: false
    });

    new Treant(chartConfig);

    $('.add-role').click(function () {
        roleFormReset();
        $('#addRoleFormModal').modal('show');
        $('#addRoleFormModal input[name="parent"]').val($(this).data('id'));
       // $('#addRoleFormModal input[name="type"]').val('C');
    });

    $('.edit-role').click(function () {
        roleFormReset();
        $('#addRoleFormModal').modal('show');
        $('#addRoleFormModal input[name="name"]').val($(this).data('name'));
        $('#addRoleFormModal textarea[name="description"]').text($(this).data('description'));
        $('#addRoleFormModal input[name="id"]').val($(this).data('id'));
        $('#addRoleFormModal input[name="parent"]').val($(this).data('parent'));
       // $('#addRoleFormModal input[name="type"]').val('C');
    });

    $('.delete-role').click(function () {
        var that = $(this);

        swal({
                title: "Jesteś pewien?",
                text: "Usunięcie roli jest procesem nieodwracalnym!",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#ed1c24",
                cancelButtonText: "Nie, zamknij",
                confirmButtonText: "Tak, usuń!",
                closeOnConfirm: true
            },
            function () {
                $('#delete-role-form input[name="node_id"]').val($(that).data('id'));
                $('#delete-role-form').submit();
                //swal("Deleted!", "Your imaginary file has been deleted.", "success");
            });

    });

    $(".add-user").click(function () {
        swal({
                title: "Czy na pewno dodać użytkownika?",
                type: "info",
                showCancelButton: true,
                //confirmButtonColor: "#ed1c24",
                cancelButtonText: "Nie",
                confirmButtonText: "Tak",
                closeOnConfirm: true
            },
            function () {

                window.location.href = "/user/add";
            });
    });

    $(".user-list").click(function () {
        that = $(this);

        $.ajax({
            type: "POST",
            url: window.ajaxUserListUrl,
            data: {'csrfmiddlewaretoken': window.csrf_token, 'id': that.data("id")},
            beforeSend: function () {
                //$("#search-box").css("background","#FFF url(LoaderIcon.gif) no-repeat 165px");
            },
            success: function (result) {

                if (result.status == 'ERROR') {
                    swal(result.message, '', 'warning');
                    return;
                }


                if (!result.hasOwnProperty('data')) {
                    console.log('no data');
                    return;
                }

                var res = $.parseJSON(result.data);

                $("table#user_list_table tbody").html(null);

                $.each(res, function (i, e) {
                    var row = $("#user_list_template").html();

                    row = row.replace("__USERADD_URL__", userAddUrl);
                    row = row.replace("__ID__", e.pk);
                    row = row.replace("__NAME_SURNAME__", e.fields.first_name + ' ' + e.fields.last_name);
                    row = row.replace("__EMAIL__", e.fields.email);
                    row = row.replace("__PERSONAL_ID__", e.fields.personal_id);
                    row = row.replace("__NIP__", e.fields.nip);

                    $("table#user_list_table tbody").append(row);
                });

                $("#userListModal .modal-title span").text(that.closest("div").children(".node-name").text());

                $('#userListModal').modal('show');


            }
        });

    });


});