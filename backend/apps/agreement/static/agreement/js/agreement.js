$(document).ready(function () {

    $(".btn-submit").click(function () {
        $("form#agreement-form").submit();
    });

    $(document).on('keyup', '#search-box', function (e) {

        if ($(this).val().length < 2) {
            return;
        }

        var ids = [];

        $("#event-user-list-row-table > tbody > tr").each(function () {
            ids.push(parseInt($(this).data("id")));
        });

        $("#suggestion-box").html(null);

        $.ajax({
            type: "POST",
            url: window.client.ajxClientlistUrl,
            data: {'key': $(this).val(), 'csrfmiddlewaretoken': window.csrf_token, 'id': JSON.stringify(ids)},
            beforeSend: function () {
                //$("#search-box").css("background","#FFF url(LoaderIcon.gif) no-repeat 165px");
            },
            success: function (result) {

                if (result.status == 'ERROR') {
                    alert(result.message);
                    return;
                }

                if (!result.hasOwnProperty('data')) {
                    return;
                }

                var list = result.data;

                var html = '<ul>';

                for (var i in list) {
                    html += '<li ';
                    html += 'data-id="' + list[i].pk + '" ';
                    html += 'data-personal_id="' + list[i].personal_id + '" ';
                    html += 'data-nip="' + list[i].nip + '" ';
                    html += 'data-name="' + list[i].first_name + ' ' + list[i].last_name + '" ';
                    // html += 'data-email="' + list[i].fields['email'] + '" ';
                    html += '>' + list[i].first_name + ' ' + list[i].last_name + '</li>';
                }

                html += '</ul>';

                $("#suggestion-box").html(html);
                $("#suggestion-box").show();
                $("#search-box").css("background", "#FFF");
            }
        });
    });

    $(document).on('click', ".suggestion-list li", function () {
        $("#suggestion-box").hide();
        var row = $("#client-list-row-template").html();
        row = row.replace(/__CLIENT_ID__/g, $(this).data('id'));
        row = row.replace("__CLIENT_NAME__", $(this).data('name'));
        row = row.replace("__CLIENT_PERSONAL_ID__", $(this).data('personal_id'));
        row = row.replace("__CLIENT_NIP__", $(this).data('nip'));

        $("#client-list-row-table tbody").html(row);
        $("#search-box").val(null);
    });
});