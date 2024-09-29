function getBrokersForAdviser(url, id, idBroker, callback) {
    "use strict";
    $.ajax(url, {
        dataType: 'json',
        method: 'POST',
        data: {'id': id, csrfmiddlewaretoken: _g.csrfmiddlewaretoken},
        success: function (res) {
            callback(res.data, idBroker);
        },
        error: function (res) {
            swal({
                title: "Błąd!",
                text: res.errMSG,
                type: 'error',
                confirmButtonText: "ok"
            });
            return false;
        }
    });
}

export default getBrokersForAdviser;
