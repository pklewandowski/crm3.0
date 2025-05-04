import Swal from "sweetalert2";

let errorTypeMapping = {
        "PermissionDenied": "You don't have permission to perform this action",
        "AttributeError": "Attribute error"
    }


class Alert {
    static formatText(text) {
        if (!Array.isArray(text)) {
            return (text);
        } else {
            let list = '<ul>';
            for (let i of text) {
                list += `<li>${i}</li>`;
            }
            list += '</ul>';
            return list;
        }
    }

    static info(title, text = '', callback = '', callbackArgs = null) {
        Swal.fire({
            html: Alert.formatText(text),
            title: title,
            icon: 'info',
            showCloseButton: true,
        }).then((result) => {
            if (!result.value) {
                return false;
            } else if (typeof callback === 'function') {
                callback(callbackArgs);
            }
        })
    }

    static question(title, text = '', callback = '', callbackArgs = null, callbackAbort = null) {
        Swal.fire({
            title: title,
            html: Alert.formatText(text),
            icon: 'question',
            showCloseButton: true,
            showCancelButton: true,
            confirmButtonText: "Tak!",
            cancelButtonText: "Nie"
        }).then((result) => {
            if (!result.value) {
                if (typeof callbackAbort === 'function') {
                    callbackAbort();
                }
                return false;
            } else if (typeof callback === 'function') {
                callback(callbackArgs);
            }
        })
    }

    static questionInput(title, text = '', callback = '', callbackArgs = null, callbackAbort = null) {
        Swal.fire({
            input: 'text',
            title: title,
            html: Alert.formatText(text),
            icon: 'question',
            showCloseButton: true,
            showCancelButton: true,
            confirmButtonText: "Tak!",
            cancelButtonText: "Nie"
        }).then((result) => {
            if (!result.value) {
                if (typeof callbackAbort === 'function') {
                    callbackAbort();
                }
                return false;
            } else if (typeof callback === 'function') {
                callback(callbackArgs);
            }
        })
    }

    static yesNoCancel(title,
                       text = '',
                       callback = '',
                       yesCallback = '',
                       noCallback = '',
                       callbackArgs = {callback: null, yesCallback: null, noCallback: null},
                       callbackAbort = null) {
        Swal.fire({
            title: title,
            html: Alert.formatText(text),
            icon: 'question',
            showDenyButton: true,
            showCloseButton: true,
            showCancelButton: true,
            confirmButtonText: "Tak!",
            denyButtonText: 'Nie',
            cancelButtonText: "Anuluj"
        }).then((result) => {
            if (result.value === undefined) {
                if (typeof callbackAbort === 'function') {
                    callbackAbort();
                }
                return;
            }
            if (result.isConfirmed) {
                if (typeof yesCallback === 'function') {
                    yesCallback(callbackArgs.yesCallback);
                }

            } else if (result.isDenied) {
                if (typeof noCallback === 'function') {
                    noCallback(callbackArgs.noCallback);
                }
            }

            if (typeof callback === 'function') {
                callback(callbackArgs.callback);
            }
        });
    }

    static questionWarning(title, text = '', callback = '', callbackArgs = null, callbackAbort) {
        Swal.fire({
            title: title,
            html: Alert.formatText(text),
            icon: 'warning',
            showCloseButton: true,
            showCancelButton: true,
            // confirmButtonText: "Tak!",
            cancelButtonText: "Anuluj"
        }).then((result) => {
            if (!result.value) {
                if (typeof callbackAbort === 'function') {
                    callbackAbort();
                }
                return false;

            } else if (typeof callback === 'function') {
                callback(callbackArgs);

                return true;
            }
        })
    }

    static questionWarningInput(title, text = '', callback = '', callbackArgs = null, callbackAbort = null) {
        Swal.fire({
            input: 'text',
            title: title,
            html: Alert.formatText(text),
            icon: 'warning',
            showCloseButton: true,
            showCancelButton: true,
            // confirmButtonText: "Tak!",
            cancelButtonText: "Anuluj"
        }).then((result) => {
            if (!result.value) {
                if (typeof callbackAbort === 'function') {
                    callbackAbort();
                }
                return false;
            }
            if (typeof callback === 'function') {
                callback(callbackArgs);
            }
        })
    }

    static warning(title, text = '', callback = '', callbackArgs = null, callbackAbort = null) {
        Swal.fire({
            title: title,
            html: Alert.formatText(text),
            icon: 'warning',
            showCloseButton: true
        }).then((result) => {
            if (!result.value) {
                if (typeof callbackAbort === 'function') {
                    callbackAbort();
                }
                return false;
            } else if (typeof callback === 'function') {
                callback(callbackArgs);
            }
        })
    }


    static error(title, text = '', callback = '', callbackArgs = null, errorType = null) {
        if (errorType) {
            title = errorTypeMapping[errorType]
        }
        Swal.fire({
            html: Alert.formatText(text),
            title: title,
            icon: 'error',
            showCloseButton: true
        }).then((result) => {
            if (!result.value) {
                return false;
            } else if (typeof callback === 'function') {
                callback(callbackArgs);
            }
        })
    }
}

export default Alert;