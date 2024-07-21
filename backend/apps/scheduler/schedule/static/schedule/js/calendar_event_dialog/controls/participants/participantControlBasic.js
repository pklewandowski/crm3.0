import {ParticipantControlBasicUtils} from "./utils/participantControlBasicUtils.js";

const ParticipantControlBasic = function (containerId, opt) {

    let _this = this;

    this.defaults = {
        controls: {
            employee: $('select[name="schedule-employee_"]'),
            client: $('select[name="schedule-client_"]'),
            service: $('select[name="schedule-service"]'),
        },
        // employeeTemplate: '<label for="employee__IDX_">Pracownik:</label><select id="employee__IDX_" name="schedule-employee_" class="form-control input-md" multiple="multiple"></select>',
        // clientTemplate: '<label for="client__IDX_">Klient:</label><select id ="client__IDX_" name="schedule-client_" class="form-control input-md" multiple="multiple"></select>',
        // serviceTemplate: '<label for="service__IDX_">Usługa:</label><select id ="service__IDX_" name="schedule-service" class="form-control input-md"></select>'
    };

    this.opt = $.extend({}, this.defaults, opt);
    this.utils = new ParticipantControlBasicUtils();

    this.container = $(`#${containerId}`);
    this.employeeTemplate = this.opt.employeeTemplate;
    this.clientTemplate = this.opt.clientTemplate;
    this.rows = [];
    this.inputTemplate =
        '<div class="participant-basic-row">' +
        `<div class="col-lg-4 service">${this.serviceTemplate}</div>` +
        `<div class="col-lg-4 nopadding-left employee">${this.employeeTemplate}</div>` +
        `<div class="col-lg-4 nopadding-left client">${this.clientTemplate}</div>` +
        '</div>';


    function _addParticipantRow() {
        let uid = guid();
        // TODO: sprawdzić, czy ostatni rząd niepusty i dopiero wtedy dodawać, jeśli pusty to nie dodawać
        // _this.container.append(_this.inputTemplate.replace(/_IDX_/g, uid));
        // _this.utils.employeeSelect2($(`#employee_${uid}`), $(`#client_${uid}`));
        // _this.utils.clientSelect2($(`#employee_${uid}`), $(`#client_${uid}`));

        _this.opt.controls.employee.prop('multiple', 'multiple');
        _this.opt.controls.client.prop('multiple', 'multiple');

        _this.utils.employeeSelect2(_this.opt.controls.employee, _this.opt.controls.client);
        _this.utils.clientSelect2(_this.opt.controls.employee, _this.opt.controls.client);
    }


    this.init = function () {
        //TODO: dodać przycisk "(+)" umożliwiający dodanie rzędu
        _addParticipantRow();
    };

    this.participant = {
        add: function () {
            _addParticipantRow();
        },

        getList: function () {
            let client = _this.opt.controls.client.val();
            let employee = _this.opt.controls.employee.val();
            let p = [];
            let master, detail;

            if (Array.isArray(employee) && Array.isArray(client)) {
                if (employee.length > 1 || client.length > 1) {
                    Alert.error('Błąd uczsetników', 'Pracownik i klient nie mogą jednocześnie zawierać wielu wpisów');
                    return [];
                }
                p.push({id: client[0], parent: employee[0]});
                p.push({id: employee[0], parent: ''});
                return p;
            }

            if (Array.isArray(client)) {
                detail = client;
                master = employee;
            } else {
                detail = employee;
                master = client;
            }
            for(let i of detail) {
                p.push({id: i, parent: master});
            }
            p.push({id: master, parent:''});
            return p;
        }
    };

    this.init();

};

export default ParticipantControlBasic;
