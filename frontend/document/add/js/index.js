import DocumentAttributeRenderer from "../../document-attribute/renderer/document-attribute-renderer";
import {DocumentAttributeRendererUtils} from "../../document-attribute/renderer/document-attribute-renderer-utils";
import DocumentAttributeForm from "../../../_core/form/documentAttributeForm";
import ajaxCall from "../../../_core/ajax";
import Alert from "../../../_core/alert";
import FormValidation from "../../../_core/form/form-validaion";
import {DocumentAnnex} from "../../js/document-annex";

window.documentAttributeDataPromises = [];

$(document).ready(() => {
    let owner;
    let formModel;
    let copyAnnexData = '';

    new DocumentAnnex();

    ajaxCall({
            method: 'get',
            url: '/document/api/',
            dataType: 'json',
            data: {typeId: _g.document.type.id, initialOwnerId: _g.document.initialOwner.id}
        },
        (resp) => {
            formModel = resp.formAttributes;
            let da = new DocumentAttributeRendererUtils();
            da._render(formModel, document.getElementById('documentData'));
            DocumentAttributeRenderer.setCalculable(formModel);
            owner = Input.getByCode('owner');

            if (_g.document.initialOwner && _g.document.initialOwner.id && _g.document.initialOwner.text) {
                owner.add(new Option(_g.document.initialOwner.text, _g.document.initialOwner.id, false, true));
                owner.dispatchEvent(new Event('select2:select'));
            }

            let responsible = Input.getByCode('responsible');
            responsible.add(new Option(`${_g.credentials.user.first_name} ${_g.credentials.user.last_name}`, _g.credentials.user.id, false, true));
        },
        (resp) => {
            Alert.error('Błąd', resp.responseJSON.errmsg);
            jsUtils.LogUtils.log(resp.responseJSON, null);
        },
        null
    );

// save procedure
    let saveCallback = (data) => {
        ajaxCall({
                method: 'post',
                url: '/document/api/',
                data: {
                    type: _g.document.type.id,
                    owner: owner.value,
                    formData: JSON.stringify(data),
                    copyAnnexData: copyAnnexData
                }
            },
            (resp) => {
                FormValidation.removeErrors();
                window.location = `/document/edit/${resp.id}`;
            },
            (resp) => {
                Alert.error(resp.responseJSON.errmsg);
                FormValidation.addErrors(resp.responseJSON.errorList);
            },
            () => {
                $(".loader-container").fadeOut();
            }
        )
    };

    document.getElementById('saveDocBtn').addEventListener('click', () => {
        FormValidation.removeErrors();
        if (!Input.isNullValue(Input.getValue(Input.getByCode('annex')))) {
            Alert.yesNoCancel(
                'Czy skopiować dane dokumentu aneksowanego?',
                '',
                () => {
                    $(".loader-container").fadeIn();
                    let attributeData = DocumentAttributeForm.collectData(formModel, '', 'FORM');
                    saveCallback(attributeData);
                },
                () => {
                    copyAnnexData = true;
                }
            )

        } else {
            $(".loader-container").fadeIn();
            let attributeData = DocumentAttributeForm.collectData(formModel, '', 'FORM');
            saveCallback(attributeData);
        }
    });
});