import Alert from "./alert";

function ajaxCall(opts, cSuccess, cError, cComplete) {
    return new Promise((resolve, reject) => {

        let defaults = {
            headers: {"X-CSRFToken": Cookies?.get('csrftoken')},
            ContentType: "application/json"
        };
        let options = Object.assign({}, defaults, opts);

        options.success = (res) => {
            if (cSuccess && typeof cSuccess == 'function') {
                resolve(cSuccess(res));
            } else {
                resolve(res);
            }
        };

        options.error = (res) => {
            if (res && (res.status == 401)) {
                window.location = '/login';
                return;
            }
            if (cError && typeof cError == 'function') {
                reject(cError(res));
            } else {
                console.log(res);
                let errmsg = res?.responseJSON?.errmsg ? res.responseJSON.errmsg :
                    res?.responseJSON?.detail ? res.responseJSON.detail : 'Niezidentyfikowany wyjątek. Proszę zgłosić błąd do administratora';
                Alert.error('błąd', errmsg);
                reject(res);
            }
        };

        options.complete = () => {
            if (cComplete && typeof cComplete == 'function') {
                cComplete();
            }
        };
        $.ajax(options);
    })
}

export default ajaxCall;