let attrFormsetTabIdPattern = 'attr_formset___ID___tab';

function setAttributeDependencyVisibility(el) {
    "use strict";
    return;
    let id = parseInt(el.data('id'));
    let val = el.val();
    $.each(el.closest('.document-section-row-body').find('[data-dependency]'), function (i, e) {
        let d = $(this).data("dependency");
        let dependency = {};
        if (typeof d === 'string') {
            dependency = JSON.parse(d.replace(/'/g, '"'));
        }

        if (dependency[id]) {
            if (el.data('attribute_disabled') || dependency[id].indexOf(val) === -1) {
                $(this).closest('.form-group').hide();
                $(this).val(null);
                $(this).data('attribute_disabled', true);
                setAttributeDependencyVisibility($(this));
            } else {
                $(this).closest('.form-group').show();
                $(this).data('attribute_disabled', false);
                setAttributeDependencyVisibility($(this));
            }
        }
    });
}

function setSubsectionName(lovElement) {
    "use strict";
    let section = lovElement.closest(".document-section-row-body");
    let cName = lovElement.closest(".repeated-section-content").data('conditional_name_attribute');
    if (!cName) {
        return;
    }
    if (lovElement.prop('name').indexOf(cName) !== -1) {
        let id = section.closest('.tab-pane').prop('id');
        $('a[href="#' + id + '"').text(lovElement.find('option:selected').text());
    }
}

function handleLov(lov) {
    "use strict";
    setSubsectionName(lov);
    setAttributeDependencyVisibility(lov);
}

function addRepeatSubsection(el, force) {
    "use strict";
    let viewType = el.data('viewtype') ? el.data('viewtype') : 'BLOCK';
    let sectionAttributes = el.data('attributes');
    let id = el.data('id');
    let parentSectionId = el.data('parent_section_id');
    let name = el.data('name');
    let conditionalNameAttribiute = el.data('conditional_name_attribute');
    let tabId = attrFormsetTabIdPattern.replace('__ID__', id);
    let tabContent = tabId + '_content';
    let tabIdPane = tabId + '_pane';
    // let container = el.closest('.document-section').find('.document-section-body');
    let container = $(`#section_${parentSectionId}`);
    let uId = guid();

    //TODO: drut!!!!! docelowo ciągnąć liTemplate z includa templatki na stronie
    let liTemplate =
        '<li data-status="NEW" class="__CLASS__">' +
        '<a data-toggle="tab" href="#' + tabIdPane + '___CNT__">' + name + '</a>' +
        '<div data-id="" class="tab-close-btn"><i class="fa fa-times"></i></div>' +
        '</li>';

    let tab = container.find('#' + tabId);
    let tmpl = $('#attr_formset_' + id + '_template').html().replace(/__ROW_UID_VALUE__/g, uId).replace(/__prefix__/g, `__prefix_${uId}__`);

    if (tab.length) {

        if (viewType === 'BLOCK') {
            tab.append(liTemplate.replace('__CLASS__', '').replace(/__CNT__/g, uId));
            container.find("#" + tabContent).append('<div data-status="NEW" id="' + tabIdPane + '_' + uId + '" class="tab-pane fade in">' + tmpl + '</div>');
        } else if (viewType === 'TABLE') {
            container.find("#" + tabContent).append(tmpl.replace('__TAB_ID_PANE__', tabIdPane + '_' + uId));
        }
    } else {
        let html = '';
        if (viewType === 'BLOCK') {
            html =
                '<ul id="' + tabId + '" class="nav nav-tabs">' +
                liTemplate.replace('__CLASS__', 'active').replace(/__CNT__/g, uId) +
                '</ul>' +
                `<div id="${tabContent}" class="tab-content pad-t repeated-section-content" data-conditional_name_attribute="${conditionalNameAttribiute}">` +
                `<div data-status="NEW" id="${tabIdPane + '_' + uId}" class="tab-pane fade in active">${tmpl}</div>` +
                '</div>';
        } else if (viewType === 'TABLE') {
            let tableSectionClass = '';
            let headerTmpl = $('#attr_formset_' + id + '_header_template').html();
            if (sectionAttributes !== null) {
                if (sectionAttributes.sortable) {
                    tableSectionClass = 'sortable-table-section';
                }
            }

            html = `<div class="panel panel-default repeated-section-content" data-conditional_name_attribute="${conditionalNameAttribiute}">` +
                `<div class="panel-heading">${name}</div>` +
                '<div class="panel-body">' +
                `<div id="${tabId}">` +
                '<table class="table table-condensed" style="position: relative;">' + headerTmpl +
                `<tbody class="${tableSectionClass}" id="${tabContent}">${tmpl.replace('__TAB_ID_PANE__', tabIdPane + "_" + uId)}</tbody>` +
                '</table>' +
                '</div>' +
                '</div>' +
                '</div>';
        }
        container.append(html);

        if (sectionAttributes && sectionAttributes.sortable) {
            $('#' + tabContent).sortable();
        }
    }

    if (!force && conditionalNameAttribiute) {
        $(`#${tabIdPane + '_' + uId}`).find(`[id$="${conditionalNameAttribiute}"]`).trigger('change');
    }

    // $('#' + tabContent).find('.document-section-row-body').find('.lov').each(function () {
    //     handleLov($(this));
    // });

    return `${tabIdPane + '_' + uId}`;
}

function addTableForm(el) {
    "use strict";
    let container = el.closest(".table-attribute-container");
    let rowContainer = container.find('table tbody');
    let parentUId = container.data('row_uid');
    let uId = guid();
    let tmpl = $(`#attr_table_formset_${el.data("id")}_template`).html()
        .replace('__ROW_UID_VALUE__', uId)
        .replace('__PARENT_ROW_UID_VALUE__', parentUId)
        .replace(/__prefix__/g, `__prefix_${guid()}__`);

    rowContainer.append(tmpl);
    rowContainer.find("tr:last").find(".autocomplete").each(function (i, e) {
        setAutocomplete($(e));
    });

    rowContainer.find("tr:last .date-field").each(function () {
        setDatePicker($(this));
    });
    rowContainer.find("tr:last .datetime-field").each(function () {
        setDatetimePicker($(this));
    });
    rowContainer.find("tr:last .time-field").each(function () {
        setTimePicker($(this));
    });

    rowContainer.find("tr:last").find('input,textarea,select').filter(':visible:first').focus();

}

function enumerateTableItems() {
    "use strict";
    let table = {};
    $(".table-attribute-container").each(function () {
        table[$(this).data('id')] = '';
    });

    $.each(Object.keys(table), function (idx, tab) {

        let cnt = parseInt($(`#id_attr-table-formset-${tab}-INITIAL_FORMS`).val());

        $.each($(`.table-attribute-container[data-id="${tab}"]`), function (i, e) {

            let _e = $(e);
            $.each(_e.find('table tbody tr'), function (i1, e1) {
                let _e1 = $(e1);
                if (_e1.data('status') === "NEW") {
                    $.each(_e1.find('input, select, textarea'), function () {
                        let name = $(this).attr('name').replace(/__prefix_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}__/g, cnt);
                        $(this).attr('name', name);
                    });
                    cnt++;
                }
            });
        });
        $(`#id_attr-table-formset-${tab}-TOTAL_FORMS`).val(cnt);
    });
}

function enumerateSubsectionItems() {
    "use strict";
    enumerateTableItems();

    $.each($('.repeat-subsection-add-btn'), function (i, e) {
        let _e = $(e);
        let cnt = 0; //$(`#id_attr-formset-${_e.data('id')}-INITIAL_FORMS`).val();

        $('#' + attrFormsetTabIdPattern.replace('__ID__', _e.data('id')) + '_content .tab-pane').each(function (i1, e1) {
            $.each($(e1).find('input, select, textarea'), function () {
                let name = $(this).attr('name').replace(/__prefix_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}__/g, cnt);
                $(this).attr('name', name);
            });
            cnt++;
        });
        $(`#id_attr-formset-${_e.data('id')}-TOTAL_FORMS`).val(cnt);
    });
}

function setAutocomplete(e) {
    e.select2({
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

function setOwnerListUrl() {
    "use strict";

    let url;
    if (_g.document && _g.document.ownerType) {
        switch (_g.document.ownerType) {
            case 'CLIENT':
                url = _g.document.url.clientsForSelect2;
                break;
            case 'EMPLOYEE':
                url = _g.document.url.employeesForSelect2;
                break;
            case 'CONTRACTOR':
                url = _g.document.url.contractorsForSelect2;
                break;
            default:
                break;
        }
        return url;
    }
}

function fitTextareaToContent() {

    $("#attribute-tab").find('textarea').each(function () {
        "use strict";
        this.style.height = this.scrollHeight + 10;
    });
}



$(document).ready(function () {

    $("#id_document-owner").select2({
        theme: 'bootstrap',
        ajax: {
            method: 'post',
            url: setOwnerListUrl(),
            dataType: 'json'
        },
        minimumInputLength: 2,
        language: "pl"
    });

    // TODO: docelowo przenieść do aplikacji attribute
    $("#attribute_toggle_notrequired_btn").click(function () {
        $.each($("#attribute-tab input, select, textarea"), function () {
            if (!$(this).attr('required')) {
                $(this).closest('.form-group').toggle('slow');
            }
        });
    });

    $("#save_doc_btn").click(function () {
        $("#add_note_modal").modal();
    });

    $("#add_doc_with_note_btn").click(function() {
        enumerateSubsectionItems();
        $('form').submit();
    });

    $(".repeat-subsection-add-btn").click(function () {
        let tabId = addRepeatSubsection($(this));
        $("#" + tabId).find(".autocomplete").each(function (i, e) {
            setAutocomplete($(e));
        });
        $("#" + tabId).find(".date-field").each(function (i, e) {
            setDatePicker($(e));
        });
    });

    $(document).on("click", ".table-formset-row-add-btn", function () {
        addTableForm($(this));
    });

    $(document).on("click", ".table-formset-row-delete-btn", function () {
        let container = $(this).closest(".table-attribute-container");
        $(this).closest("tr").remove();
        container.find('.table-formset-row-add-btn').focus();
    });

    $(document).on('click', '.tab-close-btn', function () {
        let _this = $(this);
        swal({
            title: 'Czy na pewno usunąć zakładkę?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: "Tak, usuń!",
            cancelButtonText: "Nie",
        }).then((result) => {
            if (!result.value) {
                return;
            }
            let tab = _this.closest('li');
            let tabContentPane = $(tab.find('a').attr('href'));
            let ul = _this.closest('ul');
            if (tab.data('status') === 'NEW') {
                tab.remove();
                tabContentPane.remove();
            } else {
                let prefix = tabContentPane.data('prefix');
                $("#id_" + prefix + "-DELETE").val('1');
                tab.find('a').css({'color': 'red', 'text-decoration': 'line-through'}); // TODO: DRUT!!!!!!!!! przerobić na klasę css i podmieniać
                tab.find('.tab-close-btn').hide();
                tab.find('.tab-reopen-btn').show();
            }

            if (!ul.find('li').length) {
                $('#' + ul.attr('id') + '_content').remove();
                ul.remove();
            }
        });
    });

    $(document).on('click', '.tab-reopen-btn', function () {
        "use strict";
        let _this = $(this);
        swal({
            title: 'Czy na pewno przywrócić zakładkę?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: "Tak, przywróć!",
            cancelButtonText: "Nie",
            closeOnConfirm: true,
        }).then((result) => {
            if (!result.value) {
                return;
            }
            let tab = _this.closest('li');
            let tabContentPane = $(tab.find('a').attr('href'));
            let prefix = tabContentPane.data('prefix');

            $("#id_" + prefix + "-DELETE").val('');
            tab.find('.tab-close-btn').show();
            tab.find('.tab-reopen-btn').hide();
            tab.find('a').css({'color': 'inherit', 'text-decoration': 'none'}); // TODO: DRUT!!!!!!!!! przerobić na klasę css i podmieniać
        });
    });

    $('.lov').each(function () {
        handleLov($(this));
    });

    $(document).on('change', '.lov', function () {
        handleLov($(this));
    });

    $(".autocomplete").each(function (i, e) {
        setAutocomplete($(this));
    });

    $("#generate_decision_btn").click(function () {

        swal({
            title: 'Czy na pewno wygenerować decyzję?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: "Tak, wygeneruj!",
            cancelButtonText: "Nie"
        }).then((result) => {
            if (result.value) {
                $("#loaderContainer").show();
                $.ajax({
                    url: '/report/add/',
                    method: "post",
                    data: {id: documentId},

                    success: function (res) {

                        let data = res.data;

                        row = `<tr class="report-row-first"><td>${data.name}</td><td>${data.code}</td>` +
                            `<td>${data.creation_date}</td><td>${data.created_by}</td>` +
                            `<td><div class="btn-group"><a href="/report/download-report/${data.id}/" class="btn btn-default btn-sm edit">` +
                            `<i class="fas fa-eye"></i></a></div></td></tr>`;


                        $('table#reportTab tbody tr:first-child').removeClass('report-row-first');
                        $('table#reportTab tbody').prepend(row);

                        $("#loaderContainer").hide();
                        Alert.info(`Pomyślnie wygenerowano decyzję nr ${data.code}`);
                    },

                    error: function (res) {
                        $("#loaderContainer").hide();
                        Alert.error('Wystąpił wyjątek!', res.responseJSON.errmsg);
                    }
                });
            }
        });
    });

    $('.sortable-table-section').sortable();


    $(document).on('click', '.lov-description', function () {
        "use strict";

        $(this).data('lastSelected', $(this).find('option:selected').val());
        $(this).data('lastDescription', $(this).closest('tr').find('.lov-description-target').val());

    });

    $(document).on('change', '.lov-description', function (ev) {

        if (confirm('czy na pewno zmienić dane?')) {
            let container = $(this).closest('tr');
            container.find('.lov-description-target').val($(this).find(':selected').data('description'));
        } else {
            $(this).val($(this).data('lastSelected'));
            return false;
        }
    });

    let attributePanelMode;

    $("#accordionHorizontal").click(function () {
        if (attributePanelMode !== 'H') {

            $('[id^="section_"]').each(function () {
                $(this).appendTo("#attributeHorizontal");
            });

            $("#accordion").appendTo("#attributeTabPaneHorizontal");
            $('.collapse').collapse('hide');
            attributePanelMode = 'H';
            $("#accordionHorizontal").toggleClass('fa-arrow-alt-circle-right fa-arrow-alt-circle-down');
            $(".attributePanelHorizontalContainer").show();

        } else {
            $('[id^="section_"]').each(function () {
                $(this).appendTo(`[data-section="${$(this).attr('id')}"]`);
            });
            $("#accordion").appendTo("#attribute-tab");
            $(".attributePanelHorizontalContainer").hide();
            attributePanelMode = 'V';
            $("#accordionHorizontal").toggleClass('fa-arrow-alt-circle-right fa-arrow-alt-circle-down');
        }
    });

    $('a.collapse-trigger').click(function (e) {
        if (attributePanelMode === 'H') {
            $('.collapse').collapse('hide');
        }
    });

    $("#revertStatus").click(function () {
        _this = $(this);
        Alert.questionWarning(
            'Czy na pewno cofnąć status?',
            '',
            ()=>{
                ajaxCall({
                    url: _g.document.url.revertStatus,
                    method: 'post',
                    data: {
                        id: _this.data('id'),
                        id_status: _this.data('id_status'),
                        csrfmiddlewaretoken: _g.csrfmiddlewaretoken
                    }

                },() =>{
                    window.location.reload();
                },(resp)=> {
                    let res = resp.responseJSON;
                    Alert.error('Błąd', res.errmsg);
                });
            }
        )
    });


    $(".add-user-btn").click(function () {
        $("#add_user_modal").modal();
    });

    $("#print_process_flow_btn").click(function () {
        console.log('print process');
        let _this = $(this);

        $.ajax({
            url: _g.document.url.printProcessFlow,
            method: 'post',
            data: {
                id: _this.data('id'),
                csrfmiddlewaretoken: _g.csrfmiddlewaretoken
            },

        }).done(function (resp) {
            let status_template = $("#printStatusTemplate").html();
            let html = '<table class="table table-bordered">';

            //style="width: 100%; margin: 20px; max-width: 100%; border: 1px solid #dddddd;"

            if (resp.track.length) {
                $.each(resp.track, function (i, e) {

                    let tmpl = status_template;
                    tmpl = tmpl.replace('__STATUS_NAME__', e.status.name);
                    tmpl = tmpl.replace('__CREATION_DATE__', e.status.creationDate);
                    tmpl = tmpl.replace('__CREATED_BY__', e.status.createdBy);

                    let notes = '';

                    if (e.notes.length) {
                        $.each(e.notes, function (i1, e1) {
                            notes += `<tr><td><div style="margin-left: 20px;"><span><i class="far fa-comment-alt"></i></span> ${e1.creationDate}: ${e1.createdBy}<br>${e1.text}</div></td></tr>`;
                        });
                    }


                    tmpl = tmpl.replace('__NOTES__', notes);

                    html += `${tmpl}`;
                });
                html += '</table>';

                $("#print_process_flow_modal .print-process-flow-text").html(html);
                $("#print_process_flow_modal").modal();
            }


        }).fail(function (resp) {
            let res = resp.responseJSON;
            Alert.error('Błąd', res.errmsg);
        });

        function printElement(elem) {
            var mywindow = window.open('', 'PRINT', 'height=800,width=800');


            mywindow.document.write('<html><head>');

            mywindow.document.write(`<link href="/static/resource/bootstrap/css/bootstrap.min.css" rel="stylesheet" type="text/css">`);
            mywindow.document.write(`<link href="/static/fonts/font-awesome-5.0.13/css/fontawesome-all.css" rel="stylesheet" type="text/css">`);
            // mywindow.document.write(`<style> body{-webkit-print-color-adjust:exact; color-adjust:exact; font-size: 11px;} </style>`);

            mywindow.document.write('</head><body onload="window.print();window.close();">');
            mywindow.document.write(document.getElementById(elem).innerHTML);
            // mywindow.document.write('<footer style="position: fixed; bottom: 0px; width: 100%;"><hr>CRM - wydruk przebiegu procesu </footer>');
            mywindow.document.write('</body></html>');

            mywindow.document.close(); // necessary for IE >= 10
            mywindow.focus(); // necessary for IE >= 10*/

            return true;
        }

        $("#run_print_process_flow_btn").click(function () {
            printElement('printProcessFlowContainer');
        });
    });

    $(document).on('focus input', 'textarea', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight + 10);
    });

    $(".collapse").on('shown.bs.collapse', function () {
        fitTextareaToContent();
    });

});


