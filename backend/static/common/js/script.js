function getCookie(c_name) {
    if (document.cookie.length > 0) {
        let c_start = document.cookie.indexOf(c_name + "=");
        if (c_start !== -1) {
            c_start = c_start + c_name.length + 1;
            let c_end = document.cookie.indexOf(";", c_start);
            if (c_end === -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function toogleActive(that) {
    if (that.children().hasClass('fa-check'))
        that.children().removeClass('fa-check').addClass('fa-times');
    else
        that.children().removeClass('fa-times').addClass('fa-check');
}

function setDatetimePicker(e) {
    e.datetimepicker({
        locale: 'pl',
        format: 'YYYY-MM-DD HH:mm',
        useCurrent: false
    });
    // workaround until unify calendar control: one for all items. Now we have two different calendars and need to move scheduler.schedule
    // to vanillajs-datepicker-3ws calendar
    e[0].minDate = function (minDate) {
        $(e).data("DateTimePicker").minDate(minDate);
    }
}

function setCalendarDatetimePicker(e) {
    e.datetimepicker({
        locale: 'pl',
        format: 'YYYY-MM-DD HH:mm',
        stepping: 15,
        useCurrent: false,
        // widgetParent: 'body' // raises error "datetimepicker component should be placed within a non-static positioned container" or bad position when bpdy style position: relative
        // sideBySide: true
    });
    // workaround until unify calendar control: one for all items. Now we have two different calendars and need to move scheduler.schedule
    // to vanillajs-datepicker-3ws calendar
    e[0].minDate = function (minDate) {
        $(e).data("DateTimePicker").minDate(minDate);
    }
}

function setDatePicker(e) {
    e.datetimepicker({
        locale: 'pl',
        format: 'YYYY-MM-DD',
        useCurrent: false,
        extraFormats: ['DD.MM.YYYY'],
    });

    // workaround until unify calendar control: one for all items. Now we have two different calendars and need to move scheduler.schedule
    // to vanillajs-datepicker-3ws calendar
    e[0].minDate = function (minDate) {
        $(e).data("DateTimePicker").minDate(minDate);
    }
}

function setTimePicker(e) {
    e.datetimepicker({
        format: 'HH:mm',
        stepping: 15,
        useCurrent: false,
        // widgetParent: 'body'
    });

    // e.timepicker({
    //     showMeridian:false
    // });
}

function setAutocomplete(e) {
    e.select2({
        allowClear: true,
        placeholder: 'Kliknij aby wybrać...',
        theme: 'bootstrap',
        ajax: {
            method: 'post',
            url: e.data('autocomplete_url'),
            dataType: 'json'
        },
        minimumInputLength: 2,
        language: "pl",
        width: '100%'
    });
}

function setSelect2(e) {
    e.select2({
        allowClear: true,
        placeholder: 'Kliknij aby wybrać...',
        language: "pl",
        // minimumResultsForSearch: 1
        theme: 'bootstrap'
    });
}

// function goSearch(e) {
//     e.preventDefault();
//     $("#search").val($("#search_text").val());
//     window.location = '?page=1&search=' + $("#search").val();
//     return false;
// }


function openModalDialog(e) {
    e.modal();
}

function goSearch(e) {
    // e.preventDefault();
    // $("#search").val($("#search_text").val());
    // window.location = '?page=1&search=' + $("#search").val();
    // return false;
    $("#filter-form").submit()
}

function toggleInput(input, show) {
    let container = input.closest('.form-group');
    if (show) {
        container.show(200);
    } else {
        container.hide(200);
    }
}

function guid() {
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
        s4() + '-' + s4() + s4() + s4();
}

function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
        .toString(16)
        .substring(1);
}

function isScrolledIntoView(el) {
    var rect = el.getBoundingClientRect();
    var elemTop = rect.top;
    var elemBottom = rect.bottom;

    // Only completely visible elements return true:
    // var isVisible = (elemTop >= 0) && (elemBottom <= window.innerHeight);
    // If anything is visible - return true
    var isVisible = elemTop <= window.innerHeight;
    // Partially visible elements return true:
    //isVisible = elemTop < window.innerHeight && elemBottom >= 0;
    return isVisible;
}

function timestamp(str) {
    return new Date(str).getTime();
}

let convertValuesToTime = function (values, handle) {
    let hours = 0,
        minutes = 0;

    if (handle === 0) {
        hours = convertToHour(values[0]);
        minutes = convertToMinute(values[0], hours);
        leftValue.innerHTML = formatHoursAndMinutes(hours, minutes);
        valueleft.innerHTML = values[0];
        return;
    }

    hours = convertToHour(values[1]);
    minutes = convertToMinute(values[1], hours);
    rightValue.innerHTML = formatHoursAndMinutes(hours, minutes);
    valueright.innerHTML = values[1];
};

function recountVal(val) {
    switch (val) {
        case 0:
            return '';
        case 360:
            return '6';
        case 720:
            return '12';
        case 1080:
            return '18';
        case 1440:
            return '24';
    }
}

var convertToHour = function (value) {
    return Math.floor(value / 60);
};
var convertToMinute = function (value, hour) {
    return value - hour * 60;
};
var formatHoursAndMinutes = function (hours, minutes) {
    if (hours.toString().length === 1) hours = '0' + hours;
    if (minutes.toString().length === 1) minutes = '0' + minutes;
    return hours + ':' + minutes;
};

$(document).ready(function () {

    // $('body').on('focus', ".date-field", function () {
    //     setDatePicker($(this));
    // });
    //
    // $('body').on('focus', ".datetime-field", function () {
    //     setDatetimePicker($(this));
    // });
    //
    // $('body').on('focus', ".calendar-datetime-field", function () {
    //     setCalendarDatetimePicker($(this));
    // });
    //
    // $('body').on('focus', ".time-field", function () {
    //     setTimePicker($(this));
    // });

    if(!window.documentDefinitionMode) {
        $.each($('.date-field'), function (i, e) {
            setDatePicker($(e));
        });


        $.each($('.time-field'), function (i, e) {
            setTimePicker($(e));
        });

        $.each($('.datetime-field'), function (i, e) {
            setDatetimePicker($(e));
        });

        $.each($('.calendar-datetime-field'), function (i, e) {
            setCalendarDatetimePicker($(e));
        });

        $.each($(".select2"), function () {
            setSelect2($(this));
        });
    }

    $(".btn-submit").click(function () {
        $("#loaderContainer").fadeIn();
        $("form").submit();
    });

    $(".btn-submit-filter").click(function () {
        $('form#filter-form #p3_csv').val(null);
        $("form#filter-form").submit();
    });

    if (typeof scrollBox !== 'undefined' && typeof scrollBox === 'function') {
        scrollBox();
    }


    //$.each($('.date-field'), function (i, e) {
    //   setDatePicker($(e));
    //});

    $('.modal').modal({
        keyboard: false,
        backdrop: 'static',
        show: false
    });

    if (jQuery().sortable) {
        $('.sortable').sortable({handle: '.sortable-handle'});
    }

    $("a.filter-dialog-btn").click(function () {
        $(".filter-dialog").modal();
    });

    $('.csv-btn').click(function () {
        $('form#filter-form #p3_csv').val('true');
        $('form#filter-form').submit();
    });

    $('.sort').click(function () {
        let sort_field = $(this).data('name');
        let sort_dir = '';
        if ($(this).hasClass('sort-unsorted') || $(this).hasClass('sort-up')) {
        } else {
            sort_dir = '-';
        }

        $('form#filter-form  #p3_sort_field').val(sort_field);
        $('form#filter-form  #p3_sort_dir').val(sort_dir);
        $('form#filter-form  #p3_csv').val(null);

        $('form#filter-form').submit();
    });


    $('[data-toggle="popover"]').popover();

    $('body').on('click', function (e) {
        //only buttons
        if(!e) {
            return;
        }
        if ($(e.target).data('toggle') !== 'popover'
            && $(e.target).parents('.popover.in').length === 0) {
            $('[data-toggle="popover"]').popover('hide');
        }
        //buttons and icons within buttons
        /*
        if ($(e.target).data('toggle') !== 'popover'
            && $(e.target).parents('[data-toggle="popover"]').length === 0
            && $(e.target).parents('.popover.in').length === 0) {
            $('[data-toggle="popover"]').popover('hide');
        }
        */
    });
    $(window).resize(function () {
        $('.popover').popover('hide');
    });

    $('[data-toggle="tooltip"]').tooltip();

    $(".page-search").click(function (e) {
        goSearch(e);
    });

    $(document).on('click', 'a.page-nav', function () {
        $('#filter-form').find('#id_filter-form-page').val($(this).data('page'));
        $('#filter-form').submit();
    });

    $(".toggle-side-menu-btn").click(function () {
        $("#mySidenav").toggleClass('sidenav-open');
        $("#main").toggleClass('main-open');

        if ($("#mySidenav").hasClass('sidenav-open')) {
            Cookies.set("side_menu_state", "open");
        } else {
            Cookies.set("side_menu_state", 'close');
        }
    });
});


// var gKeyCodes = {esc: 27, shift: 16, crtl: 17, alt: 18};

