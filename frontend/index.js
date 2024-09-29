import './_core/scss/core.scss';
import './_core/jqueryExt/jqueryExt';

import "./dist/jsUtils-bundle";
import "./dist/formUtils-bundle";

import './_core/font/roboto/Roboto-Regular.ttf';
import './_core/font/roboto/Roboto-Bold.ttf';
import './_core/font/roboto/RobotoCondensed-Regular.ttf';
import './_core/font/roboto/RobotoCondensed-Bold.ttf';
import {QuickMenu} from "./widget/quickMenu/js/quick-menu";


window.Input = jsUtils.Input;
window.Alert = jsUtils.Alert;
window.ajaxCall = jsUtils.ajaxCall;

window.evtChanged = new Event('documentEvt:changed', {bubbles: true});
window.evtRepeatableSectionCreated = new Event('documentEvt:repeatableSectionCreated', {bubbles: true});

window.debug = function (message) {
    if (LOG_LEVEL == '__DEBUG__') {
        console.log(message)
    }
};

function clearLoaders() {
    $(".loader-container").hide();
    for (let i of Array.from(document.querySelectorAll('i'))) {
        i.classList.remove('rotate-btn');
    }
}


window.onerror = (msg, url, lineNo, columnNo, error) => {
    const resizeObserverLoopErrRe = /^[^(ResizeObserver loop limit exceeded)]/;
    if (resizeObserverLoopErrRe.test(error.message)) {
        return false
    }
    clearLoaders();
    console.log(error);
    Alert.error('Wystąpił wyjątek systemowy!', msg);
};

// document.addEventListener('click', (evt) => {
//     if (!evt.target.classList.contains('error-container')) {
//         for (let i of Array.from(document.querySelectorAll('.error-container'))) {
//             i.style.display='none';
//         }
//     }
// });

// window.addEventListener( "pageshow", function ( event ) {
//   var historyTraversal = event.persisted ||
//                          ( window.PerformanceNavigation.type === 2 );
//   if ( historyTraversal ) {
//     // Handle page restore.
//     window.location.reload();
//   }
// });

_g.saved = true;
_g.urls = {downloadReportUrl: "/report/download/__REPORT_ID__/"};

window.core = {
    downloadReport: function (reportId) {
        window.location.href = _g.urls.downloadReportUrl.replace("__REPORT_ID__", reportId);
    }
};

document.addEventListener('change', (e) => {
    _g.saved = false;
    document.dispatchEvent(new Event('documentEvt:changed'));
});

$(document).on('dp.change', (e) => {
    _g.saved = false;
    document.dispatchEvent(new Event('documentEvt:changed'));
});

// hide all layers of dropdown type when clicked outside
document.addEventListener('mousedown', (e) => {
    if (e.target.closest('.dropdown-layer')) {
        return;
    }
    for (let i of Array.from(document.querySelectorAll('.dropdown-layer'))) {
        if (i !== e.target) {
            i.style.display = 'none';
        }
    }
});
// Select2 events handler
$(document).on('select2:clear', (e) => {
    e.target.dispatchEvent(new Event('change'));
});

window.addEventListener('resize', (e) => {
    for (let i of Array.from(document.querySelectorAll('.dropdown-layer'))) {
        if (i !== e.target) {
            i.style.display = 'none';
        }
    }
});

function padTo2Digits(num) {
    return num.toString().padStart(2, '0');
}

Date.prototype.addDays = function (days) {
    let date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
};

Date.prototype.defaultFormat = function () {
    return [
        this.getFullYear(),
        padTo2Digits(this.getMonth() + 1),
        padTo2Digits(this.getDate())
    ].join('-');
};

let quickMenu = new QuickMenu(350);
quickMenu.addItem('Klienci', ['fas', 'fa-user-friends'], '/client/list', '#b6d3ef');
quickMenu.addItem('Pracownicy', ['fas', 'fa-user'], '/employee/list', '#a0f686');
quickMenu.addItem('Doradcy', ['fas', 'fa-user-graduate'], '/adviser/list', '#fac09f');
quickMenu.addItem('Pośrednicy', ['fas', 'fa-people-arrows'], '/broker/list', '#d1cbf3');
quickMenu.addItem('Wnioski', ['fas', 'fa-book'], '/document/type/list', '#a2d3c3');
quickMenu.addItem('Windykacja', ['fas', 'fa-bolt'], '/document/vindication/list/1', '#ffa6a6');
quickMenu.addItem('Kalendarz', ['far', 'fa-calendar-alt'], '/schedule-app/', '#b9f3f3');
quickMenu.render();

document.addEventListener("DOMContentLoaded", (evt) => {
    let quickMenuBtn = document.querySelector('.quick-menu-btn');

    quickMenuBtn.addEventListener('click', () => {
        let quickMenu = document.getElementById('quickMenuContainer');
        if (quickMenu.style.display != 'none') {
            quickMenu.style.display = 'none';
            sessionStorage.setItem('qmDisplay', 'none');
        } else {
            quickMenu.style.display = 'block';
            sessionStorage.setItem('qmDisplay', 'block');
        }
    });

    // for (let el of Array.from(document.querySelectorAll('.input-format-currency'))) {
    //     Input.setMask(el, 'currency');
    // }
});
