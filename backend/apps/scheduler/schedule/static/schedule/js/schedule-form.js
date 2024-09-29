function resetDefinedLocationTitle() {
    $('#defined_location_title').data('id', null);
    $('#defined_location_title').text(null);
}

function disableMeetingRoom(val) {
    let el = $('form#schedule-form input:radio[name="schedule-meeting_room"][value="' + val + '"]');
    el.prop('checked', false);
    el.attr('disabled', true);
    el.closest('label').addClass('disabled');
    if (val === $('#defined_location_title').data('id')) {
        resetDefinedLocationTitle();
    }
}

function enableMeetingRoom(val) {
    let el = $('form#schedule-form input:radio[name="schedule-meeting_room"][value="' + val + '"]');
    el.removeAttr('disabled');
    el.closest('label').removeClass('disabled');
}

function getFormMode() {
    return $("form#schedule-form #basic_form_container").is(':visible') ? "basic" : "advanced";
}

function toggleFormMode() {
    return getFormMode() === 'basic' ? 'advanced' : 'basic';
}


function triggerEventActionCallback(callback) {
    "use strict";

    //TODO: docelowo zrobić obioekt ScheduleForm i property actionCallback, którą będize ustawiała dana akcja
    let messageText = $("#schedule-form #id_message-text");
    let dlg=$("#confirmEventWithNoteModal");

    dlg.modal();
    dlg.find("#eventNote").val(messageText.val());
    dlg.find(".confirm-btn").unbind('click').click(function () {
        if (typeof callback === 'function') {
            messageText.val(dlg.find("#eventNote").val());
            callback();
        }
    });
}

let sheduleUserManager = function () {

}