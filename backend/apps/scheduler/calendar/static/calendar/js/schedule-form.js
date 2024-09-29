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
    return getFormMode()=='basic' ? 'advanced': 'basic';
}