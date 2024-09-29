/**
 * All calendar template client side events handling
 * @type {string}
 */

var calendar_mode = 'event';
var ajxUserSearch;
var gFilter;



function getUserFromIframe() {
    alert('getUserFromIframe');
}

$(document).ready(function () {


    $(".checkbox-multiselect").multiselect({
        includeSelectAllOption: true,
        allSelectedText: 'wybrano wszystkie',
        numberDisplayed: 0,
        buttonWidth: '100%',
        buttonText: function (options, select) {
            let totalOptLength = select.find('option').length;
            if (options.length === 0) {
                return 'Nie wybrano żadnej opcji'
            } else if (options.length === totalOptLength)
                return 'Wybrano wszystkie';
            else {
                return 'Wybrano: ' + options.length;
            }
        }
    });

    $(document).keyup(function (e) {
        if (e.keyCode === gKeyCodes.esc) { //27
            $(".tooltip").tooltip("hide");
            $('.popover').popover("hide");
        }
    });

    $("#datepicker11").datetimepicker({
        locale: "pl",
        inline: true,
        format: 'YYYY-MM-DD'
    });

    $("#datepicker11").on('dp.change', function (e) {
        $("#calendar").fullCalendar('gotoDate', e.date.format('YYYY-MM-DD'));
    });

    $('#addScheduleFormModal').modal({
        keyboard: false,
        backdrop: 'static',
        show: false
    });

    $(document).on('click', '#submit-btn', function () {
        triggerEventActionCallback(function () {
            "use strict";
            // setProductRetail();
            $('form#schedule-form').submit();
        });
    });

    $(document).on('click', '#confirm-btn', function () {
        confirmEvent($("form#schedule-form #id").val(), $("form#schedule-form #id_user").val());
    });

    $(document).on('click', '#reject-btn', function () {
        rejectEvent($("form#schedule-form #id").val(), $("form#schedule-form #id_user").val());
    });

    $(document).on('click', ".suggestion-list li.user-list", function () {
        var participant_type;
        var u = [];

        $.each($(this).data(), function (i, e) {
            u[i] = e;
        });

        $("#suggestion-box").hide();

        swal({
            title: 'Typ uczestnictwa',
            text: "Wybierz typ uczestnictwa",
            type: 'info',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Prowadzący',
            cancelButtonText: 'Uczestnik',
            confirmButtonClass: 'btn btn-primary',
            cancelButtonClass: 'btn btn-default',
            buttonsStyling: false
        }).then((result) => {
            if (!result.value) {
                participant_type = 'P'; // P - participant
            } else {
                participant_type = 'L'; // L - leader
            }

            u['participant_type'] = participant_type;
            u['active'] = false;

            if ($('form#schedule-form #id_schedule-type option:selected').data('exclusive_participant_mode') === 'True') {
                u['exclusive_participant_mode'] = true;
            } else {
                u['exclusive_participant_mode'] = false;
            }

            $("#event-user-list-row-table tbody").append(fillParticipantList(u));
            $("#search-box").val(null);
        });
    });

    $(document).on('click', '#event-user-list-row-table > tbody > tr a.delete', function () {

        let _this = $(this);

        swal({
            title: 'Jesteś pewien?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: "Tak, usuń uczestnika!",
            confirmButtonColor: "#DD6B55",
            cancelButtonText: "Nie"
        }).then((result) => {
            console.log(result.value);
            if (result.value) {
                _this.parents('tr').remove();
                swal("Użytkownik został usunięty!", "", "success");
            }
        });
    });

    $(document).on('keyup', '#search-box', function (e) {

        let ids = [];

        $("#event-user-list-row-table").find("tbody > tr").each(function () {
            ids.push(parseInt($(this).data("id")));
        });

        $("#suggestion-box").html(null);

        let key = $(this).val();
        if (key.length < 2) {
            return;
        }

        if (ajxUserSearch) {
            ajxUserSearch.abort();
        }

        ajxUserSearch = $.ajax({
            type: "POST",
            url: window.calendar.ajxUserListUrl,
            data: {key: key, csrfmiddlewaretoken: window.csrf_token, id: JSON.stringify(ids)},
            beforeSend: function () {
                //$("#search-box").css("background","#FFF url(LoaderIcon.gif) no-repeat 165px");
            },
            success: function (result) {

                if (result.status === 'ERROR') {
                    alert(result.message);
                    return;
                }

                if (!result.hasOwnProperty('data')) {
                    return;
                }

                let userList = $.parseJSON(result.data);
                let html = '<ul>';

                for (let i in userList) {
                    html += '<li class="user-list" ';
                    html += 'data-id="' + userList[i].pk + '" ';
                    html += 'data-first_name="' + userList[i].fields['first_name'] + '" ';
                    html += 'data-last_name="' + userList[i].fields['last_name'] + '" ';
                    html += 'data-email="' + userList[i].fields['email'] + '" ';
                    html += 'data-phone_one="' + userList[i].fields['phone_one'] + '" ';
                    html += 'data-phone_two="' + userList[i].fields['phone_two'] + '" ';
                    // html += 'data-confirmed="' + userList[i].fields['confirmed'] + '" ';
                    html += 'data-confirmed="false" ';
                    html += '>' + userList[i].fields['first_name'] + ' ' + userList[i].fields['last_name'] + '</li>'
                }

                html += '</ul>';

                let suggestion_box = $("#suggestion-box");
                suggestion_box.html(html);
                suggestion_box.show();

                $("#search-box").css("background", "#FFFFFF");
            }
        });
    });

    $(document).on('change', '#id_schedule-headquarter', function () {
        $(".meeting-room-select-buttons .headquarter-meeting_room-container").hide();
        $('.meeting-room-select-buttons #headquarter_' + $(this).val()).fadeIn(500)
    });

// $("#id_employee-user").select2({
//     ajax: {
//         method: 'post',
//         url: '/schedule/get-clients-for-meeting-filter/',
//         dataType: 'json'
//     },
//     minimumInputLength: 2,
//     language: "pl"
// });

    $("#id_filter-user").select2({
        theme: 'bootstrap',
        ajax: {
            method: 'post',
            url: '/schedule/get-users-for-meeting-filter/',
            dataType: 'json'
        },
        minimumInputLength: 2,
        language: "pl"
    });

    $("#id_filter-employee").select2({
        theme: 'bootstrap',
        ajax: {
            method: 'post',
            url: '/schedule/get-employees-for-meeting-filter/',
            dataType: 'json'
        },
        minimumInputLength: 2,
        language: "pl"
    });


    $("#" + schedule_type_id).change(function () {
        var el = $(this).find(':selected');

        if (el.data('single_person') === "True") {
            $(".users-panel").hide(200);
        } else {
            $(".users-panel").show(200);
        }

        if (el.data('location_required') === "False") {
            $(".location-panel").hide(200);
        } else {
            $(".location-panel").show(200);
        }

        if (el.data('title_required') === "False") {
            $("#id_title").prop("disabled", true);
            if (el.data('default_title')) {
                $("#id_title").data('default_title', "True");
                $("#id_title").val(el.data('default_title'));
            }
        } else {
            $("#id_title").prop("disabled", false);
            if ($("#id_title").data('default_title') === "True") {
                $("#id_title").val(null);
            }
            $("#id_title").data('default_title', "False");
        }
    });

    $('#scheduleFilterForm #filterBtn').click(function (e) {
        let filterForm = $("#scheduleFilterForm");

        gFilter = {
            text: filterForm.find("#eventFilterPhrase").val(),
            scheduleTypes: filterForm.find("#scheduleTypes").val(),
            scheduleStatuses: filterForm.find("#scheduleStatuses").val(),
        };
        $("#scheduleFilterResetBtn").show();
        refetchEvents();
        $("#filterTabHeader a").css('background-color', 'red').css({"color": "#ffffff"});
        // $('#scheduleFilterModal').modal('toggle');
    });

    $("#scheduleFilterResetBtn").click(function () {
        let filterForm = $("#scheduleFilterForm");
        gFilter = {
            text: '',
            scheduleTypes: [],
            scheduleStatuses: [],
        };
        refetchEvents();
        $("#filterTabHeader a").css('background-color', 'inherit').css({"color": "inherit"});
        filterForm.find("#eventFilterPhrase").val(null)
        filterForm.find("#scheduleTypes").multiselect('selectAll', false).multiselect('updateButtonText');
        filterForm.find("#scheduleStatuses").multiselect('selectAll', false).multiselect('updateButtonText');
        $("#scheduleFilterResetBtn").hide();

    });

    $(document).on('shown.bs.collapse', '#eventLocationCollapse', function () {
        google.maps.event.trigger(map, 'resize');
    });


    function setCyclical() {
        "use strict";

        let scheduleForm = $("#schedule-form");
        let daysOfMonth = scheduleForm.find('#id_schedule-days_of_month');
        let daysOfWeek = scheduleForm.find('#id_schedule-days_of_week');
        let cyclical = scheduleForm.find('#id_schedule-is_cyclical');
        let repeatPeriod = scheduleForm.find('#id_schedule-repeat_period');
        let monthdaysList = $("#cyclicMonthdaysPanel ul");
        let weekdaysList = $("#cyclicWeekdaysPanel ul");

        if (cyclical.is(':checked')) {
            if (repeatPeriod.val() === 'WEEK') {
                let days = [];
                $.each(weekdaysList.find('li.cyclical-day-active '), function () {
                    days.push($(this).data('value'))
                });
                daysOfWeek.val(days.join('|'));
            } else if (repeatPeriod.val() === 'MC') {
                let days = [];
                $.each(monthdaysList.find('li.cyclical-day-active '), function () {
                    days.push($(this).data('value'))
                });
                daysOfMonth.val(days.join('|'));
            }
        } else {
            daysOfMonth.val(null);
            daysOfWeek.val(null);
        }
    }

    $(document).on('submit', 'form#schedule-form', function (event) {
        event.preventDefault();
        let scheduleForm = $("#schedule-form");
        let mode = getFormMode();
        if (!mode) {
            throw('No form mode specified!')
        }
        $('form#schedule-form #id_schedule-mode').val(mode);

        if (mode === 'basic') {
            scheduleForm.find('#id_schedule-host_user_').val(scheduleForm.find('#id_schedule-employee_').val())
        }
        scheduleForm.find(".form-field-error").removeClass('form-field-error');
        scheduleForm.find("ul.errorlist").remove();
        scheduleForm.find("#error_list").text(null).hide();

        setCyclical();

        create_post();
    });

    $('#delete-btn').click(function () {
        deleteEvent($('form#schedule-form #id').val());
    });

    $(document).on('change', 'form#schedule-form #id_schedule-type', function () {
        setEventFormAccess(false);
    });

    $(document).on("change", "#toggle_all_types_chk", function () {
        $(".event-type-chk").attr("checked", $(this).is(':checked'));
    });

    $(document).on("click", "#event-user-list-row-table tbody tr a.participant-confirmation i.active", function () {
        toggleParticipantConfirmation($(this));
    });

    $(document).on('click', "#close-btn", function () {
        triggerEventActionCallback(function () {
            "use strict";
            statusEvent($('form#schedule-form #id').val(), window.id_user, 'CL', true);
        });
    });

    $(document).on('click', "#cancel-btn", function () {
        triggerEventActionCallback(function () {
            "use strict";
            statusEvent($('form#schedule-form #id').val(), window.id_user, 'AN', true);
        });
    });

    $(document).on('click', "#cancel_and_set-btn", function () {
        triggerEventActionCallback(function () {
            "use strict";

            let schedule_form = $('form#schedule-form');

            statusEvent(schedule_form.find('#id').val(), window.id_user, 'AN', false, function () {
                schedule_form.find("#cancel-btn").hide();
                schedule_form.find("#cancel_and_set-btn").hide();
                schedule_form.find("#close-btn").hide();
                schedule_form.find("#delete-btn").hide();
                schedule_form.find("#activate-btn").hide();

                schedule_form.find('input#id').val(null);
                schedule_form.find('input#id_schedule-start_date').val(null);
                schedule_form.find('#start_date').val('09:00');
                schedule_form.find('input#id_schedule-end_date').val(null);
                schedule_form.find('#end_date').val('17:00');
            });
        });
    });

    $(document).on('click', "#activate-btn", function () {
        triggerEventActionCallback(function () {
            "use strict";
            statusEvent($('form#schedule-form #id').val(), window.id_user, 'NW', true);
        });

    });

    $(document).on('click', "#delete-btn", function () {
        triggerEventActionCallback(function () {
            "use strict";
            statusEvent($('form#schedule-form #id').val(), window.id_user, 'DL', true);
        });
    });

    $(document).on('click', "#delete_and_set-btn", function () {
        triggerEventActionCallback(function () {
            let schedule_form = $('form#schedule-form');

            statusEvent(schedule_form.find('#id').val(), window.id_user, 'DL', false, function () {
                gCancelActionBtnHtml = '';
                gSaveActionBtnHtml = gActionBtn.submit;
                schedule_form.find('#cancelMenu').hide();
                schedule_form.find("#closeAndSetBtn").hide();
                schedule_form.find("#close-btn").hide();
                schedule_form.find("#closeAndSetBtn").hide();

                schedule_form.find('input#id').val(null);
                schedule_form.find('input#id_schedule-start_date').val(null);
                schedule_form.find('#start_date').val('09:00');
                schedule_form.find('input#id_schedule-end_date').val(null);
                schedule_form.find('#end_date').val('17:00');
                schedule_form.find('#id_schedule-type').find('option').removeAttr('disabled');
            });
        });
    });

    $(document).on('click', "#closeAndSetBtn", function () {
        triggerEventActionCallback(function () {
            let schedule_form = $('form#schedule-form');

            statusEvent(schedule_form.find('#id').val(), window.id_user, 'CL', false, function () {
                gCancelActionBtnHtml = '';
                gSaveActionBtnHtml = gActionBtn.submit;
                schedule_form.find('#cancelMenu').hide();
                schedule_form.find("#close-btn").hide();
                schedule_form.find("#closeAndSetBtn").hide();

                schedule_form.find('input#id').val(null);
                schedule_form.find('input#id_schedule-start_date').val(null);
                schedule_form.find('#start_date').val('09:00');
                schedule_form.find('input#id_schedule-end_date').val(null);
                schedule_form.find('#end_date').val('17:00');
                schedule_form.find('#id_schedule-type').find('option').removeAttr('disabled');
            });
        });
    });

    $(document).on('click', '.suggestion-list ul.user-func li', function () {
        $.fancybox.open({
            href: $("#add_user_btn").data('url') + $(this).data('type') + "/?iframe=1",
            type: 'iframe',
            padding: 5,
            helpers: {
                overlay: {closeClick: false} // prevents closing when clicking OUTSIDE fancybox
            }
        });
    });

    $(document).on('change', 'input:radio[name="schedule-meeting_room"]', function () {
        if ($(this).closest('label').hasClass('disabled')) {
            return false;
        }
        $("#defined_location_title").text($(this).data('name'));
        $("#defined_location_title").data('id', $(this).val());
    });

    $(document).on('click', '#custom_location-btn', function () {
        $('#defined_location_title').text(null);
        $('#defined_location_title').data('id', $("input[name='schedule-meeting_room']:checked").val());
        $("form#schedule-form input[name='schedule-meeting_room']").prop('checked', false);
        $("form#schedule-form input[name='schedule-meeting_room']").closest('label').removeClass('active');


        $("#event-defined-location-panel").slideUp();
        $("#event-custom-location-panel").slideDown();
        google.maps.event.trigger(map, "resize");
    });

    $(document).on('click', '#defined_location-btn', function () {
        var mval = $('#defined_location_title').data('id');
        if (mval) {
            $("input[name='schedule-meeting_room']").each(function () {
                if ($(this).val() == mval) {
                    $(this).prop('checked', true);
                    $(this).closest('label').addClass('active');
                    $('#defined_location_title').data('id', null);
                    $('#defined_location_title').text($(this).data('name'));
                    clear_form_elements('#custom-location-address');
                    return false;
                }
            });

        }
        $("#event-defined-location-panel").slideDown();
        $("#event-custom-location-panel").slideUp();
    });

    $(document).on('change', 'form#schedule-form input[name="users-invited_users_exclusive_participant_mode_label"]', function () {
        if ($(this).is(':checked')) {
            $(this).closest('tr').find('input[name="users-invited_users_exclusive_participant_mode"]').val('1');
        } else {
            $(this).closest('tr').find('input[name="users-invited_users_exclusive_participant_mode"]').val('0');
        }
    });

    $(document).on('click', 'a#add_event_message_btn', function () {
        $("#event_message_text_container").slideDown();
    });

    $("#firstAvailableEventBtn").click(function () {
        getAvailableDates();
    });

    $(document).on('click', '#available_date_list a', function () {
        let dt = $(this).data('date');
        $("#calendar").fullCalendar('gotoDate', dt);
        $('#available_date_modal').modal('hide');
    });


    $("#available_date_reset_btn").click(function () {
        clear_form_elements($('#available_date_form'));
        calendar_mode = 'event';
        let calendarControl = $('#calendar');
        calendarControl.fullCalendar('refetchEvents');
        calendarControl.fullCalendar('gotoDate', Date.now());
        calendarControl.fullCalendar('refetchEvents');
        $('#available_date_form').find('#id_filter-min_duration option:first').prop('selected', true);
        $("#available_date_reset_btn").hide();
    });

    $(document).on('click', "#mode_toggle_btn", function () {
        $(this).unbind('click');
        let mode = toggleFormMode();

        $("#form_content").hide({
            duration: 'slow',
            complete: function () {
                getFormContent(mode);
                setEventFormAccess();
                initMap();
                $("#form_content").show('slow');
            }
        });
    });

    let productRetail = new ProductRetail(
        {
            urls: {
                productsForCategoryUrl: '/product-retail/get-products-for-category/', //TODO: docelowo url ze zmiennej globalnej od {% static ... %}
                productCategoryTreeUrl: '/product-retail/get-category-tree/'
            }
        });

    $(document).on('click', '.product-retail-add-btn', function () {
        $('#getProductRetailModal').modal();
        productRetail.getCategoryTree();
    });

    $(document).on('click', '.remove-retail-product-btn', function () {
        let _this = $(this);
        swal({
            title: 'Jesteś pewien?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: "Tak, usuń produkt!",
            confirmButtonColor: "#DD6B55",
            cancelButtonText: "Nie"
        }).then((result) => {
            if (!result.value) {
                return;
            }
            _this.closest('tr').remove();
        });
    });

    $(document).on('click', '#getProductRetailModal #productList table tbody tr', function () {

    });

    $(document).on('click', '.add-product-to-list-btn', function () {

        let tmpl = $("#productClientFormsetTemplate");
        if (!tmpl) {
            throw "productClientFormsetTemplate not found"
        }

        let row = $(this).closest('tr');
        let idProduct = row.data('id');

        if ($(".product-retail-list").find(`tr[data-id="${idProduct}"]`).length) {
            Alert.info('Ten produkt został już dodany do listy', '', 'info');
            return;
        }

        let unitPrice = row.find('td.unit-price').text();
        let productName = row.find('td.product-name').text();
        let html = tmpl.html().replace(/__ID_PRODUCT__/g, idProduct).replace(/__UNIT_PRICE__/g, unitPrice).replace(/__PRODUCT_NAME__/g, productName);

        $("#product_retail_list").find('table tbody').append(html)
    });

    $("#toggleEventType").change(function () {
        $('.filter-event-type').prop('checked', $(this).prop("checked"));
    });

    $(document).on('change', '#id_schedule-is_cyclical', function () {
        if ($(this).is(':checked')) {
            $("#cyclicSettingsBtn").show(200);
        } else {
            $("#cyclicSettingsBtn").hide(200);
        }
    });

    $(document).on('click', '#cyclicSettingsBtn', function () {
        $("#cyclicalSettingsModal").modal();
    });

    $(document).on('click', 'ul.cyclical-days li', function () {
        $(this).toggleClass('cyclical-day-active');
    });

    $(document).on('change', '#id_schedule-repeat_period', function () {
        if (['WEEK', '2WEEK'].includes($(this).val())) {
            $('#cyclicMonthdaysPanel').hide(200);
            $('#cyclicWeekdaysPanel').show(200);
        } else if ($(this).val() === 'MC') {
            $('#cyclicMonthdaysPanel').show(200);
            $('#cyclicWeekdaysPanel').hide(200);
        }
    });
});

