$(document).ready(function () {
    $('.sticky-note').click(function () {
        console.log('sticky click');
    });

    $('.sticky-note').draggable({
        start: function (event, ui) {
            $(this).addClass('sticky-note-drag');
        },
        stop: function (event, ui) {
            $(this).removeClass('sticky-note-drag');
        }
    });

    $('.sticky-notes-container').stickyNotes();

    $('#mnu_sticky_note_toggle').click(function () {
        $('.sticky-notes-container').stickyNotes('toggle');
    });

    $('#mnu_sticky_note_add').click(function () {
        $('.sticky-notes-container').show();
        $('.sticky-notes-container').stickyNotes('add');
    });

    // $(".datepicker").datetimepicker({
    //     locale: "pl",
    //     inline: false,
    //     format: 'YYYY-MM-DD'
    // });


    $(".form-action-messages");
    $("#page_content").fadeIn(1000);

    // $('.action-button-container .btn-success').click(function () {
    //     console.log('action-button-container .btn-success');
    //     $(this).prop('disabled', true);
    // });

    $(document).on("submit", "form", function (e) {
        "use strict";
        $(".btn-success").prop('disabled', true);
    });


    $(document).on("click", "#id_notifications .dropdown-menu", function (e) {
        "use strict";
        e.stopPropagation();
    });

    $(document).on("click", ".close-notification-btn", function (e) {
        let cnt = document.querySelector('.notification-count');
        console.log(cnt);

        Alert.questionWarning(
            'Czy na pewno usunąć powiadomienie?',
            'Usunięcie powiadomienia spowoduje, że nie będzie ono wyświetlane na liście',
            () => {
                let _this = $(this);
                let tr = $(this).closest('tr');
                let id = tr.data('id');

                ajaxCall({
                        method: "post",
                        url: _g.notifications.urls.close,
                        data: {id: id}
                    },
                    (resp) => {
                        tr.remove();
                        cnt.innerHTML = parseInt(cnt.innerHTML) - 1;
                    },
                    (resp) => {
                        // LogUtils.log(resp.responseJSON);
                    });
            })
    });
});
