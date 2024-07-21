import DocumentAttribute from "../../document/document-attribute/document-attribute";
import DocumentAttachment from "./document-attachment";
import DocumentAttributeForm from "../../_core/form/documentAttributeForm";
import Alert from "../../_core/alert";
import ajaxCall from "../../_core/ajax";
import DirectoryTree from "../../_core/controls/directory-tree";

import Report from "../../report/js/report";
import FormValidation from "../../_core/form/form-validaion";
import {DocumentNotes} from "../notes/js/notes";
import {DocumentAnnex} from "./document-annex";
import {ProductDashboard} from "../../product/js/financePack/dashboard/js/product-dashboard";
import {Product} from "../../product/js/product";
import {calculateProductAggregates} from "../../product/js/financePack/calculation/calculation";
import {DateUtils} from "../../_core/utils/date-utils";

function revertStatus() {
    Alert.questionWarning(
        'Czy na pewno cofnąć status?',
        '',
        () => {
            ajaxCall(
                {
                    url: _g.document.urls.revertStatus,
                    method: 'post',
                    data: {
                        id: _g.document.id,
                        id_status: _g.document.status.id
                    }
                },
                () => {
                    window.location.reload();
                },
                (resp) => {
                    let res = resp.responseJSON;
                    Alert.error('Błąd', res.errmsg);
                });
        });
}

function saveData(e) {
    e.querySelector('i').classList.add('rotate-btn');
    $(".loader-container").fadeIn();
    ajaxCall(
        {
            method: 'put',
            url: '/document/api/',
            data: {
                document: _g.document.id,
                attributes: JSON.stringify(DocumentAttributeForm.collectData(window.documentAttribute.renderer.model.model)),
                status: document.getElementById('id-documentStatus').value
            },
        },
        (res) => {
            e.classList.remove('document-changed');
            Alert.info('Pomyślnie zapisano dane!', '', () => {
                _g.saved = true;
                if (res.documentStatus) {
                    window.location.reload();
                }
            });
        },
        null,
        () => {
            e.querySelector('i').classList.remove('rotate-btn');
            $(".loader-container").fadeOut();
        }
    );
}

// function setAttributeDependencyVisibility(el) {
//     "use strict";
//     let id = parseInt(el.data('id'));
//     let val = el.val();
//     $.each(el.closest('.document-section-row-body').find('[data-dependency]'), function (i, e) {
//         let d = $(this).data("dependency");
//         let dependency = {};
//         if (typeof d === 'string') {
//             dependency = JSON.parse(d.replace(/'/g, '"'));
//         }
//
//         if (dependency[id]) {
//             if (el.data('attribute_disabled') || dependency[id].indexOf(val) === -1) {
//                 $(this).closest('.form-group').hide();
//                 $(this).val(null);
//                 $(this).data('attribute_disabled', true);
//                 setAttributeDependencyVisibility($(this));
//             } else {
//                 $(this).closest('.form-group').show();
//                 $(this).data('attribute_disabled', false);
//                 setAttributeDependencyVisibility($(this));
//             }
//         }
//     });
// }

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

window.documentAttributeDataPromises = [];
window.dateUtils = DateUtils;

$(document).ready(() => {
    let doc = new Document();
    //Initiate product instalment schedules container
    //todo: finally it should be the part of product financial pack plugin activated by plugin loader mechanism
    window.schedule = {
        evt: {
            scheduleRefresh: 'scheduleEvt:refresh'
        },
        items: []
    };

    let availableStatuses;
    let processFlow;
    let errorList = {};

    // set attachments and attributes
    window.documentAttribute = new DocumentAttribute(
        'documentAttributeContainer',
        {
            id: _g.document.id,
            status: _g.document.status.id,
            type: _g.document.type.id
        },
        errorList
    );
    window.attachment = new DocumentAttachment(_g.document.id, 'attachmentContainer');
    window.directoryTree = new DirectoryTree("atmDirectoryTree", _g.document.id, _g.document.code, {attachment: window.attachment});
    window.report = new Report('reportModal');

    let reportForm = new formUtils.Form(
        document.getElementById('reportEditForm'),
        null,
        null,
        null,
        {reloadOnSave: true}
    );

    ajaxCall({
            method: 'get',
            url: '/document/api/',
            dataType: 'json',
            data: {id: _g.document.id}
        },
        (resp) => {
            availableStatuses = resp.availableStatuses;
            processFlow = resp.processFlow;

            if (Array.isArray(availableStatuses) && availableStatuses.length) {
                let el = document.getElementById('availableStatuses');
                let statusElement = document.getElementById('id-documentStatus');

                availableStatuses.map((e) => {
                    let inner = `<i class="fas fa-arrow-alt-circle-right available-statuses-list-arrow"></i>${e.available_status.name}`;
                    let li = jsUtils.Utils.domElement('li', null, null, null, e.available_status.id.toString(), null, inner);
                    if (e.available_status.is_alternate) {
                        li.classList.add('document-status-alternate');
                    }

                    li.addEventListener('click', e => {
                        statusElement.value = e.target.value;
                        saveData(document.getElementById('changeStatusBtn'));
                    });

                    el.appendChild(li);
                });

                document.querySelector('.available-statuses-btn-container').style.display = 'inherit';
            }
        },
        (resp) => {
            Alert.error('Błąd', resp.responseJSON.errmsg);
            console.log(resp.responseJSON);
        },
    );


    // save procedure
    let saveDocBtn = document.getElementById('saveDocBtn');
    if (saveDocBtn) {
        document.getElementById('saveDocBtn').addEventListener('click', function (e) {
            saveData(document.getElementById('saveDocBtn'));
        });
    }

    // add report procedure
    for (let i of Array.from(document.querySelectorAll('.report-list-menu li a'))) {
        i.addEventListener('click', (e) => {
            report.get(i.dataset['templateid']);
        });
    }

    document.addEventListener('documentEvt:changed', (e) => {
        if (saveDocBtn) {
            saveDocBtn.classList.add('document-changed');
        }
    });

    $("#revertStatus").click(function () {
        revertStatus();
    });

    document.addEventListener('documentAttributeEvt:afterAttributesRender', () => {
        let documentAnnex = new DocumentAnnex();
        documentAnnex.setAnnex();
        FormValidation.addErrors(errorList);

        // todo: DRUT JAK CHUJ
        // if (document.getElementById('3370')) {
        //     ClassicEditor
        //         .create(document.getElementById('3370'),
        //             {
        //                 language: 'pl',
        //                 // toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'undo', 'redo'],
        //                 toolbar: ['bold', 'italic', 'link', 'bulletedList', 'numberedList', 'undo', 'redo'],
        //                 // heading: {
        //                 //     options: [
        //                 //         {model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph'},
        //                 //         {model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1'},
        //                 //         {model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2'},
        //                 //         {model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3'}
        //                 //     ]
        //                 // }
        //             })
        //         .then(editor => {
        //             editor.model.document.on('change', (e) => {
        //                 document.dispatchEvent(new Event('change'));
        //             });
        //             if (_g.document.editors) {
        //                 _g.document.editors['3370'] = editor;
        //             } else {
        //                 _g.document.editors = {'3370': editor}
        //             }
        //         })
        //         .catch(error => {
        //             console.error(error);
        //         });
        // }
    });

    let notes = new DocumentNotes(document.getElementById('notesContainer'), _g.document.id);
    notes.get();

    if (_g.document.product.id) {
        let product = new Product(_g.document.product.id);
        let productDashboard;

        product.getData().then(() => {
            if (product.data?.calculation_last && typeof product.data.calculation_last == 'object') {
                let dashboardData = Object.assign(product.data.calculation_last, calculateProductAggregates(product));

                productDashboard = new ProductDashboard(
                    product.id,
                    'productDashboardContainer',
                    'productDashboardTemplate',
                    dashboardData
                );
                productDashboard.bindData();
            }
        });
    }

    // TODO: DRUT!!!!!!!!!!!!
    document.addEventListener('scheduleSectionEvt:created', evt => {
        let aggregates = evt.detail.instalmentSchedule.aggregates;
        let interest_aggregate = 0.0;
        if (!aggregates) {
            return;
        }

        interest_aggregate = aggregates.instalment_interest_aggregate;

        let commissionValue = parseFloat(Input.getValue(Input.getByCode('3658'), 0));
        Input.setValue(Input.getByCode('3662'), commissionValue + interest_aggregate);

        console.log('evt instalment schedule created', evt.detail.instalmentSchedule);

    });

    document.getElementById('reportTab')?.addEventListener('click', (evt) => {
        let el = evt.target;
        if (el.classList.contains('edit')) {
            reportForm.getData(el.closest('tr').dataset['id']);
            reportForm.show(false, true);
        }

        if (el.classList.contains('delete')) {
            Alert.questionWarning('Czy na pewno usunąć pismo?', '', () => {
                ajaxCall({
                        method: 'delete',
                        url: _g.document.report.urls.reportApiUrl,
                        data: {id: el.closest('tr').dataset['id']}
                    },
                    () => {
                        el.closest('tr').remove();
                    },
                    (resp) => {
                        Alert.error('Błąd!', resp.responseJSON?.errmsg ? resp.responseJSON.errmsg : resp.responseText);
                    });
            });
        }
    });

    $('.lov').each(function () {
        handleLov($(this));
    });

    $(document).on('change', '.lov', function () {
        handleLov($(this));
    });
});
