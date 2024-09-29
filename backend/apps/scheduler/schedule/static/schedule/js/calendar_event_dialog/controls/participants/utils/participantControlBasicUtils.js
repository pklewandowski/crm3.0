const Cb = function () {

};

const ParticipantControlBasicUtils = function (opt) {
    let _this = this;
    this.prototype = Object.create(Cb);

    this.defaults = {
        employeeDataUrl: '/schedule/get-employees-for-meeting-filter/',
        clientDataUrl: '/schedule/get-clients-for-meeting-filter/',
        ALLOW_MULTIPLE_USER_CHOICE: true,
        SCHEDULE_OWNED_CLIENTS_ONLY: false,
    };

    this.opt = $.extend({}, this.defaults, opt);

    this.setClientList = function (employee, client) {

        $.ajax({
            method: 'post',
            url: '/client/get-clients-for-adviser-select2/',
            dataType: 'json',
            data: {
                id: employee.val()
            }
        }).done(function (res) {
            client.empty();
            client.select2(
                {
                    // allowClear: true,
                    placeholder: "Wybierz klienta",
                    theme: 'bootstrap', data: res
                });
            client.val(null).trigger('change');
        }).fail(function (res) {
            console.log(res.responseJSON.errmsg);
        });
    }


    function userSelect2Unselect(evt, el, item, callback, employee, client) {
        $(el).find(`option[value=${evt.params.data.id}]`).remove();

        if (!item.prop('multiple')) {
            item.select2('destroy');
            item.prop('multiple', 'multiple');
            callback(employee, client);
        }
    }

    function userSelect2Select(e, item, callback, employee, client) {
        if (e.options.length > 1) {
            item.select2('destroy');
            item.prop('multiple', '');
            let opt = item.find("option:first-child");
            item.find("option").remove();
            item.append(opt);
            callback(employee, client);
        } else {

        }
    }

    this.employeeSelect2 = function (employee, client) {
        employee.select2({
            theme: 'bootstrap',
            ajax: {
                method: 'post',
                url: _this.opt.employeeDataUrl,
                dataType: 'json'
            },
            minimumInputLength: 2,
            language: "pl",
            width: '100%'
        }).change(function (a) {
            if (_this.opt.ALLOW_MULTIPLE_USER_CHOICE) {

            }
            if (_this.opt.SCHEDULE_OWNED_CLIENTS_ONLY) {
                _this.setClientList(employee, client);
            }

        }).on('select2:selecting', function (e) {
            if (!$(this).prop('multiple')) {
                $(this).find(`option[value!=${e.params.args.data.id}]`).remove();
            }

        }).on('select2:unselect', function (e) {
            userSelect2Unselect(e, this, client, _this.clientSelect2, employee, client)

        }).on('select2:select', function () {
            userSelect2Select(this, client, _this.clientSelect2, employee, client);
        });
    };

    this.clientSelect2 = function (employee, client) {
        let s;
        if (_this.opt.SCHEDULE_OWNED_CLIENTS_ONLY) {

            s = client.select2({
                theme: 'bootstrap',
                minimumInputLength: 2,
                language: "pl",
                width: '100%'
            });
        } else {
            s = client.select2({
                theme: 'bootstrap',
                minimumInputLength: 2,
                language: "pl",
                width: '100%',
                ajax: {
                    method: 'post',
                    url: _this.opt.clientDataUrl,
                    dataType: 'json',
                    data: function (params) {
                        return {
                            q: params.term,
                            idEmployee: employee.val()
                        }
                    },
                }
            })
        }

        s.on('select2:selecting', function (e) {
            if (!$(this).prop('multiple')) {
                $(this).find(`option[value!=${e.params.args.data.id}]`).remove();
            }

        }).on('select2:unselect', function (e) {
            userSelect2Unselect(e, this, employee, _this.employeeSelect2, employee, client)

        }).on('select2:select', function () {
            userSelect2Select(this, employee, _this.employeeSelect2, employee, client);
        });
    };

    function init() {
    }

    init();
};


export {ParticipantControlBasicUtils};